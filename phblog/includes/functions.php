<?php

function sanitize_path($path) {
    return preg_replace('/\.\.\//', '', $path);
}

function crtrim($h, $s) {
    if (substr($h, -strlen($s)) === $s) {
        return substr($h, 0, strlen($h) - strlen($s));
    }
    return $h;
}

function cltrim($h, $s) {
    if (substr($h, 0, strlen($s)) === $s) {
        return substr($h, strlen($s));
    }
    return $h;
}

function img($path, $alt = '') {
    echo "<img src='image.php?name=" . sanitize_path($path) . "' alt='" . $alt . "'>";
}

function load_post($name) {
    $post = false;

    $filename = 'posts/' . sanitize_path($name);
    // Check for the file with '.post' appended
    if (!file_exists($filename) && file_exists($filename . '.post')) {
        $filename .= '.post';
    }

    ob_start();
    include $filename;
    $content = ob_get_clean();
    if (!$content) {
        return null;
    }

    return [
        'name' => $name,
        'title' => isset($TITLE) ? $TITLE : 'Untitled',
        'date' => isset($DATE) ? $DATE : 'Unknown',
        'author' => isset($AUTHOR) ? $AUTHOR : 'Unknown',
        'content' => $content,
    ];
}

function save_post($name, $title, $date, $author, $content) {
    $name = sanitize_path($name);
    $filename = '/posts/' . $name . '.post';
    $file = fopen($_SERVER['DOCUMENT_ROOT'] . $filename, 'w');
    if (!$file) {
        return null;
    }

    fwrite($file, "<?php\n");
    fwrite($file, "\$TITLE='$title';\n");
    fwrite($file, "\$DATE='$date';\n");
    fwrite($file, "\$AUTHOR='$author';\n");
    fwrite($file, "?>\n");
    fwrite($file, $content);
    fclose($file);

    return [
        'name' => $name,
        'title' => $title,
        'date' => $date,
        'author' => $author,
        'content' => $content,
    ];
}
