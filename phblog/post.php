<?php
include_once("includes/functions.php");

include_once("templates/header.php");

if (isset($_GET['name'])) {
    $post = load_post($_GET['name']);

    if ($post) {
        echo "<h1>" . $post['title'] . "</h1>";
        echo "<p><small>" . $post['date'] . " by " . $post['author'] . "</small></p>";
        echo "<p>" . nl2br($post['content']) . "</p>"; // Convert newlines to <br>
    } else {
        echo "<p>Post not found.</p>";
    }
} else {
    echo "<p>No post specified.</p>";
}

include_once("templates/footer.php");