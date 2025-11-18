<?php
include_once("includes/functions.php");
include_once("templates/header.php");

?>

<h1>Blog Posts</h1>
<form method="get">
    <input type="text" name="query" placeholder="Search...">
    <input type="submit" value="Search">
</form>

<?php
$search = isset($_GET['query']) ? "*".$_GET['query']."*" : "*";
$lines = [];
$listing = exec("ls -l posts/$search.post", $lines);
$posts = array_reverse($lines);
foreach ($posts as $post_name) {
    $post_name = basename($post_name);

    if (strpos($post_name, 'secret') !== false) {
        continue; // Skip secret files in listing
    }
    $post = load_post($post_name);
    if (!$post) {
        continue; // Skip invalid files in listing
    }
    echo "<h2><a href='post.php?name=" . crtrim($post_name, '.blog') . "'>" . $post["title"] . "</a></h2>";
    echo "<p>" . $post["date"] . " by " . $post["author"] . "</p>";
}

include_once("templates/footer.php");