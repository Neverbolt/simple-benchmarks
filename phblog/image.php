<?php
include_once("includes/functions.php");

if (!isset($_GET['name'])) {
    echo "<p>No image specified.</p>";
    exit;
}

$path = $_GET['name'];

include_once(sanitize_path($path));
