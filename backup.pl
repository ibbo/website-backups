use Archive::Zip qw( :ERROR_CODES :CONSTANTS);
use POSIX qw/strftime/;

my $zip = Archive::Zip->new();

# Add everything to the zip file.
$zip->addTree('.', '');

my $today = strftime('%Y_%m_%d_%H%M%S', localtime);
my $filename = 'website_full_backup_' . $today . '.zip';
unless ( $zip->writeToFileNamed($filename) == AZ_OK ) {
    die 'Could not write zip file';
}
