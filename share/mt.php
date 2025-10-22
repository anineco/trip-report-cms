<?php
$home = '/home/anineco'; # CONFIG: user's home directory
$cf = parse_ini_file($home . '/.my.cnf');
$dsn = "mysql:dbname=$cf[database];host=$cf[host];charset=utf8mb4;readOnly=1";
$options = [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES => false,
];
try {
    $dbh = new PDO($dsn, $cf['user'], $cf['password'], $options);
} catch (PDOException $e) {
    http_response_code(500); # Internal Server Error
    exit;
}

# Usage(example):
#   mt.php?id=396
# or
#   mt.php?lat=35.360277&lon=138.727227

$id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT, [
    'options' => ['min_range' => 1]
]);
if (!isset($id) || $id === false) {
    #
    # search nearest mountain by latitude/longitude
    #
    $lat = filter_input(INPUT_GET, 'lat', FILTER_VALIDATE_FLOAT, [
        'options' => ['min_range' => -90, 'max_range' => 90]
    ]);
    $lon = filter_input(INPUT_GET, 'lon', FILTER_VALIDATE_FLOAT, [
        'options' => [ 'min_range' => -180, 'max_range' => 180]
    ]);
    if (!isset($lat, $lon) || $lat === false || $lon === false) {
        $dbh = null;
        http_response_code(400); # Bad Request
        exit;
    }

    # CONFIG: set search radius (meters)
    $sql = <<<'EOS'
SET @EPS=100
EOS;
    $dbh->exec($sql);

    # set center point @g
    # NOTE: 'axis-order=long-lat' is required for MySQL 8 and later
    $sql = <<<'EOS'
SET @g=ST_GeomFromText(?, 4326, 'axis-order=long-lat')
EOS;
    $sth = $dbh->prepare($sql);
    $sth->execute(["POINT($lon $lat)"]);
    $sth = null;

    # find nearest mountain within the search radius
    # NOTE: ST_Distance_Sphere() is available at MySQL 8 and later
    $sql = <<<EOS
SELECT id, s.kana, s.name, alt, lat, lon,
    FORMAT(ST_Distance_Sphere(pt, @g), 1) AS distance
FROM geom
JOIN sanmei AS s USING (id)
WHERE ST_Within(pt, ST_Buffer(@g, @EPS)) AND type<=1
ORDER BY distance, type
LIMIT 1
EOS;
    $sth = $dbh->query($sql);
    $output = $sth->fetch();
    $sth = null;
} else {
    #
    # search mountain by ID
    #
    $sql = <<<'EOS'
SELECT id, s.kana, s.name, alt, lat, lon,
    '0.0' AS distance
FROM geom
JOIN sanmei AS s USING (id)
WHERE id=? AND type<=1
ORDER BY type
LIMIT 1
EOS;
    $sth = $dbh->prepare($sql);
    $sth->execute([$id]);
    $output = $sth->fetch();
    $sth = null;
}

if ($output) {
    $id = $output['id'];
    #
    # add aliases
    #
    $sql = <<<'EOS'
SELECT kana, name
FROM sanmei
WHERE id=? AND type>1
EOS;
    $sth = $dbh->prepare($sql);
    $sth->execute([$id]);
    $output['aliases'] = $sth->fetchAll();
    $sth = null;
    #
    # add prefectures
    #
    $sql = <<<'EOS'
SELECT code, name, qid
FROM city
WHERE code IN (
    SELECT DISTINCT CONCAT(LEFT(code, 2), '000')
    FROM location
    WHERE id=?
)
ORDER BY code
EOS;
    $sth = $dbh->prepare($sql);
    $sth->execute([$id]);
    $output['prefectures'] = $sth->fetchAll();
    $sth = null;
    #
    # add municipalities
    #
    $sql = <<<'EOS'
SELECT code, name, qid
FROM city
JOIN location USING (code)
WHERE id=?
ORDER BY code
EOS;
    $sth = $dbh->prepare($sql);
    $sth->execute([$id]);
    $output['municipalities'] = $sth->fetchAll();
    $sth = null;
} else {
    $output = new stdClass();
}
$dbh = null;
header('Content-Type: application/json; charset=UTF-8');
header('Cache-Control: no-store, max-age=0');
echo json_encode($output, JSON_UNESCAPED_UNICODE), PHP_EOL;
# __END__
