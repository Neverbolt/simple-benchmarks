<?php
session_start();
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    header('Location: login.php');
    exit;
}

include_once("../includes/functions.php");

include_once("../templates/header.php");

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $title = $_POST['title'];
    $date = date('Y-m-d');
    $author = $_SESSION['username'];
    $content = $_POST['content'];
    // turn title into slug
    $slug = $date . "-" . strtolower(str_replace(' ', '-', $title));
    $post = save_post($slug, $title, $date, $author, $content);
    if (!$post) {
        echo "<p>Error saving post</p>";
    } else {
        echo "<p>Post published at <a href='/post.php?name=" . $post['name'] . "'>" . $post['name'] . "</a></p>";
    }
    include_once("../templates/footer.php");
    die();
}
?>

<form method="post">
    <label for="title">Title:</label><br>
    <input type="text" id="title" name="title"><br>
    <label for="content">Content:</label><br>
    <textarea id="content" name="content"></textarea><br>
    <input type="submit" value="Create Post">
</form>

<?php
include_once("../templates/footer.php");