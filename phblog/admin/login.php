<?php
session_start();

// Simple form displayed when not logged in
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    list($username, $hashedPassword) = explode(',', file_get_contents('credentials.txt'), 2);
    if ($_POST['username'] !== trim($username)) {
        echo "<p>Username not found in credentials.txt</p>";
    } else if ($_POST['password'] !== trim($hashedPassword)) {
        echo "<p>Password not valid for user</p>";
    } else {
        $_SESSION['loggedin'] = true;
        $_SESSION['username'] = $_POST['username'];
        header('Location: index.php');
        exit;
    }
}

if (isset($_SESSION['loggedin']) && $_SESSION['loggedin'] === true) {
    header('Location: index.php');
    exit;
}

include_once("../templates/header.php");
?>

<form method="post">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <input type="submit" value="Login">
</form>

<?php
include_once("../templates/footer.php");