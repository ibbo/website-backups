#!/usr/bin/php
<?php
require __DIR__ . '/vendor/autoload.php';

use Mailgun\Mailgun;

use Google\Cloud\Storage\StorageClient;

// Parse command-line options.
$shortopts = "t"; // -t Test mode, don't upload or email anything
$longopts = array("no-upload", "no-email"); // --no-upload don't upload anything, --no-email don't send any emails
$options = getopt($shortopts, $longopts);

$doUpload = true;
$sendEmail = true;
if (array_key_exists("t", $options)) {
    $doUpload = false;
    $sendEmail = false;
}

if (array_key_exists("no-upload", $options)) {
    $doUpload = false;
}

if (array_key_exists("no-email", $options)) {
    $sendEmail = false;
}

$credsFile = 'credentials/app_creds.json';
$credsString = file_get_contents($credsFile);
$credsObj = json_decode($credsString, true);

register_shutdown_function('errorHandler', $credsObj['mailgunkey'], $sendEmail);

$databasename = 'joomladb';
$datetime = date("Y_m_d_His");
$databaseBackupName = "database-backup-$datetime";
$ext = ".sql";
$databaseBackupFile = "/tmp/$databaseBackupName$ext";

$siteZipName = "$datetime-site-full_backup";
$zipExt = '.zip';
$siteZipFile = "/tmp/$siteZipName$zipExt";

$finalMessage = "";
$finalMessage = logAndAppendMessage("Dumping sql\n", $finalMessage);

$user = $credsObj['dbuser'];
$password = $credsObj['dbpassword'];
exec("mysqldump --user=$user --password=$password --host=localhost $databasename > $databaseBackupFile");

$finalMessage = logAndAppendMessage("Creating zip of site\n", $finalMessage);
zipfile("/var/www/html/", $siteZipFile);

if ($doUpload) {
    $projectId = 'rscds-youth-branch-main-server';

    $finalMessage = logAndAppendMessage("Uploading to Google Cloud Storage\n", $finalMessage);

    $gcs = new StorageClient([
        'projectId' => $projectId
    ]);

    $bucketName = 'rscds-youth-website-backups';
    $file = fopen($databaseBackupFile, 'r');
    $bucket = $gcs->bucket($bucketName);
    $resultDatabaseObj = $bucket->upload($file, [
        'name' => "$databaseBackupName$ext"
    ]);
    $resultDatabase = $resultDatabaseObj->gcsUri();

    $file = fopen($siteZipFile, 'r');
    $resultSiteObj = $bucket->upload($file, [
        'name' => "$siteZipName$zipExt"
    ]);
    $resultSite = $resultSiteObj->gcsUri();

    $finalMessage = logAndAppendMessage("Upload succeeded\nDeleting temporary files\n", $finalMessage);
} else {
    $finalMessage = logAndAppendMessage("Upload skipped\n", $finalMessage);
    $resultDatabase = "Test Database";
    $resultSite = "Test Site";
}


unlink($databaseBackupFile);
unlink($siteZipFile);

$finalMessage = logAndAppendMessage("Backup complete\n", $finalMessage);

$body = "Website backup successful. Results: \n"
    . $finalMessage . "\n\n"
    . "Database file: " 
    . $resultDatabase . "\n"
    .  "Site file: "
    . $resultSite . "\n";

$mailgunKey = $credsObj['mailgunkey'];
if ($sendEmail) {
    emailMessage('Website backup success', $body, $mailgunKey);
} else {
    echo($body);
}

function logAndAppendMessage($msg, $fullString) {
echo $msg;
return $fullString . $msg;
}

function emailMessage($subject, $msg, $key) {
    $mailgun = new Mailgun($key);
    $domain = "mail.rscds-youth.org";
    $mailgun->sendMessage($domain, array(
        'from' => 'Website Backups <website@rscds-youth.org>',
        'to' => '<info@rscds-youth.org>',
        'subject' => $subject,
        'text' => $msg
    ));
}

function errorHandler($key, $sendEmail) { 
    $error = error_get_last();
    $type = $error['type'];
    $message = $error['message'];
    if ($type = 64 && !empty($message)) {
        echo "
            <strong>
              <font color=\"red\">
              Fatal error captured:
              </font>
            </strong>
        ";
        echo "<pre>";
        print_r($error);
        echo "</pre>";
        if ($sendEmail) {
            emailMessage('Website backup failed','Fatal error captured: \n' . $error, $key);
        }
    }
}

function zipfile($the_folder, $zip_file_name) {
//Don't forget to remove the trailing slash

$za = new FlxZipArchive;

$res = $za->open($zip_file_name, ZipArchive::CREATE);

if($res === TRUE) {
    $za->addDir($the_folder, basename($the_folder));
    $za->close();
}
else
    echo 'Could not create a zip archive';
}

/**
* FlxZipArchive, Extends ZipArchiv.
* Add Dirs with Files and Subdirs.
*
* <code>
*  $archive = new FlxZipArchive;
*  // .....
*  $archive->addDir( 'test/blub', 'blub' );
* </code>
*/
class FlxZipArchive extends ZipArchive {
    /**
     * Add a Dir with Files and Subdirs to the archive
     *
     * @param string $location Real Location
     * @param string $name Name in Archive
     * @author Nicolas Heimann
     * @access private
     **/

    public function addDir($location, $name) {
        $this->addEmptyDir($name);

        $this->addDirDo($location, $name);
     } // EO addDir;

    /**
     * Add Files & Dirs to archive.
     *
     * @param string $location Real Location
     * @param string $name Name in Archive
     * @author Nicolas Heimann
     * @access private
     **/

    private function addDirDo($location, $name) {
        $name .= '/';
        $location .= '/';

        // Read all Files in Dir
        $dir = opendir ($location);
        while ($file = readdir($dir))
        {
            // Exclude the "data" directory because it's taking to long to zip up.
            if ($file == '.' || $file == '..' || $file == 'data') continue;

            // Rekursiv, If dir: FlxZipArchive::addDir(), else ::File();
            $do = (filetype( $location . $file) == 'dir') ? 'addDir' : 'addFile';
            $this->$do($location . $file, $name . $file);
        }
    } // EO addDirDo();
}

?>
