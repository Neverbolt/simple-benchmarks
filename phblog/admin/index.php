<?php
session_start();
if (!isset($_SESSION["loggedin"]) || $_SESSION["loggedin"] !== true) {
    header("Location: /admin/login.php");
    exit();
}

include_once "../templates/header.php";
?>

<h1>Admin Dashboard</h1>
<p>Welcome to the admin area!</p>
<a href='new-post.php'>Create New Post</a> | <a href='logout.php'>Logout</a>

<?php include_once "../templates/footer.php";
