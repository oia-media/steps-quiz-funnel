<?php
/**
 * STEPS Specialty Coffee Bar - Lead Capture & Loyalty Card API Endpoint
 */

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method Not Allowed']);
    exit;
}

$rawInput = file_get_contents('php://input');
$data = json_decode($rawInput, true);

if (!$data || !is_array($data)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid JSON payload']);
    exit;
}

$name = trim($data['name'] ?? '');
$mobile = trim($data['mobile'] ?? '');
$passId = trim($data['passId'] ?? '');
$matchedDrink = trim($data['matchedDrink'] ?? 'iced_spanish_latte');
$answers = $data['answers'] ?? [];

if (mb_strlen($name) < 2 || mb_strlen($name) > 120) {
    http_response_code(422);
    echo json_encode(['success' => false, 'message' => 'Please provide a valid full name.']);
    exit;
}

// Clean & normalize Egyptian mobile number
$cleanMobile = preg_replace('/[\s\-()._]/', '', $mobile);
if (strpos($cleanMobile, '+20') === 0) {
    $cleanMobile = '0' . substr($cleanMobile, 3);
} elseif (strpos($cleanMobile, '0020') === 0) {
    $cleanMobile = '0' . substr($cleanMobile, 4);
} elseif (strpos($cleanMobile, '20') === 0 && strlen($cleanMobile) === 12) {
    $cleanMobile = '0' . substr($cleanMobile, 2);
} elseif (preg_match('/^1[0125][0-9]{8}$/', $cleanMobile)) {
    $cleanMobile = '0' . $cleanMobile;
}

// Strictly validate 11 digits starting with 010, 011, 012, or 015
if (!preg_match('/^01[0125][0-9]{8}$/', $cleanMobile)) {
    http_response_code(422);
    echo json_encode(['success' => false, 'message' => 'Please provide a valid Egyptian mobile number (11 digits starting with 010, 011, 012, or 015).']);
    exit;
}

$suffix = substr($cleanMobile, 3);
$seqs = ['01234567', '12345678', '23456789', '34567890', '45678901', '98765432', '87654321', '76543210'];
$isSequential = false;
foreach ($seqs as $s) {
    if (strpos($suffix, $s) !== false) {
        $isSequential = true;
        break;
    }
}
$isRepeated = preg_match('/(\d)\1{4,}/', $suffix) || count(count_chars($suffix, 1)) < 4;

if ($isSequential || $isRepeated) {
    http_response_code(422);
    echo json_encode(['success' => false, 'message' => "{$cleanMobile} is an invalid sequential or dummy test number. Please enter a genuine Egyptian mobile."]);
    exit;
}

$cardsFile = __DIR__ . '/../cards_db.json';
$cardsDb = [];
if (file_exists($cardsFile)) {
    $content = file_get_contents($cardsFile);
    $decoded = json_decode($content, true);
    if (is_array($decoded)) {
        $cardsDb = $decoded;
    }
}

$nowIso = date('c');
$drinkNames = [
    'iced_spanish_latte' => ['name' => 'Iced Spanish Latte', 'desc' => 'Silky espresso combined with sweet condensed milk, served over chilled ice.'],
    'strawberry_matcha' => ['name' => 'Strawberry Matcha', 'desc' => 'Ceremonial Japanese green tea layered over sweet handcrafted strawberry puree.'],
    'passionfruit_mojito' => ['name' => 'Passionfruit Mojito', 'desc' => 'Zesty passionfruit, crushed mint and sparkling fruit soda with crisp citrus notes.'],
    'mocha_frappe' => ['name' => 'Mocha Frappe', 'desc' => 'Blended ice, rich espresso, and decadent dark chocolate topped with cold velvet cream.']
];
$drinkIcons = [
    'iced_spanish_latte' => '☕',
    'strawberry_matcha' => '🍵',
    'passionfruit_mojito' => '🍹',
    'mocha_frappe' => '🥤'
];
$matchedIcon = $drinkIcons[$matchedDrink] ?? '☕';

$bannedFile = __DIR__ . '/../banned_phones.json';
$bannedPhones = file_exists($bannedFile) ? (json_decode(file_get_contents($bannedFile), true) ?: []) : [];
if (isset($bannedPhones[$cleanMobile]) || (isset($cardsDb[$cleanMobile]) && !empty($cardsDb[$cleanMobile]['isBanned']))) {
    http_response_code(403);
    echo json_encode([
        'success' => false,
        'isBanned' => true,
        'message' => 'This mobile number has been suspended from the STEPS Loyalty Program. Please speak with store management.'
    ]);
    exit;
}

if (isset($cardsDb[$cleanMobile])) {
    http_response_code(409);
    echo json_encode([
        'success' => true,
        'alreadyRegistered' => true,
        'message' => 'You have already completed the quiz! Directing you to your loyalty card...',
        'card' => $cardsDb[$cleanMobile]
    ]);
    exit;
}

$archivedFile = __DIR__ . '/../archived_cards_db.json';
$archivedDb = file_exists($archivedFile) ? (json_decode(file_get_contents($archivedFile), true) ?: []) : [];

if (isset($archivedDb[$cleanMobile])) {
    $oldCard = $archivedDb[$cleanMobile];
    unset($archivedDb[$cleanMobile]);
    file_put_contents($archivedFile, json_encode($archivedDb, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), LOCK_EX);

    if ($name) {
        $oldCard['name'] = $name;
    }
    $oldCard['isBanned'] = false;
    $oldCard['bannedAt'] = null;
    $oldCard['updatedAt'] = $nowIso;
    $oldCard['restoredAt'] = $nowIso;

    $cardsDb[$cleanMobile] = $oldCard;
    file_put_contents($cardsFile, json_encode($cardsDb, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), LOCK_EX);

    echo json_encode([
        'success' => true,
        'restored' => true,
        'message' => 'Welcome back, ' . $oldCard['name'] . '! Your loyalty card and perks have been restored.',
        'card' => $oldCard
    ]);
    exit;
}

$passIdGenerated = $passId ?: ('STP-' . strtoupper(substr(md5(uniqid()), 0, 4)) . '-26');
$cardsDb[$cleanMobile] = [
    'phone' => $cleanMobile,
    'name' => $name,
    'passId' => $passIdGenerated,
    'matchedDrink' => $matchedDrink,
    'matchedDrinkName' => $drinkInfo['name'],
    'matchedDrinkDesc' => $drinkInfo['desc'],
    'cardActive' => false,
    'stamps' => [
        '1' => ['title' => 'Free ' . $drinkInfo['name'], 'desc' => 'Your Quiz Signature Match • 100% Free Drink', 'icon' => $matchedIcon, 'status' => 'available', 'unlockedAt' => $nowIso, 'redeemedAt' => null],
        '2' => ['title' => '20% Off Pastry', 'desc' => 'Fresh Bakery Item', 'icon' => '🥐', 'status' => 'locked', 'unlockedAt' => null, 'redeemedAt' => null],
        '3' => ['title' => 'Free Size Upgrade', 'desc' => 'Coffee or Specialty Drink', 'icon' => '🥛', 'status' => 'locked', 'unlockedAt' => null, 'redeemedAt' => null],
        '4' => ['title' => 'Buy 1 Get 1 Free', 'desc' => 'Signature Drinks', 'icon' => '🎁', 'status' => 'locked', 'unlockedAt' => null, 'redeemedAt' => null],
        '5' => ['title' => 'Free Drink + VIP Status', 'desc' => 'Grand Loyalty Reward', 'icon' => '🌟', 'status' => 'locked', 'unlockedAt' => null, 'redeemedAt' => null]
    ],
    'createdAt' => $nowIso,
    'quizFinishedAt' => $nowIso,
    'activatedAt' => null,
    'updatedAt' => $nowIso,
    'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown'
];
file_put_contents($cardsFile, json_encode($cardsDb, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), LOCK_EX);

// Also append to leads.csv
$csvFile = __DIR__ . '/../leads.csv';
$csvExists = file_exists($csvFile);
$fp = fopen($csvFile, 'a');
if ($fp) {
    if (!$csvExists) {
        fputcsv($fp, ['Timestamp', 'Name', 'Phone', 'Pass ID', 'Matched Drink', 'IP']);
    }
    fputcsv($fp, [
        $nowIso,
        $name,
        $cleanMobile,
        $cardsDb[$cleanMobile]['passId'],
        $drinkInfo['name'],
        $_SERVER['REMOTE_ADDR'] ?? 'unknown'
    ]);
    fclose($fp);
}

echo json_encode([
    'success' => true,
    'message' => 'Digital loyalty card ready',
    'card' => $cardsDb[$cleanMobile]
]);
