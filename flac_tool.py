import argparse
import errno
import os
import subprocess

FLAC_EXT = ".flac"
ART_EXT = ".jpg"
OGG_EXT = ".ogg"

OGG_CMD = 'oggenc'

parser = argparse.ArgumentParser(description="Utility to mirror music directory.")
parser.add_argument('flac', help='Base path to flac files.')
parser.add_argument('ogg', help='Base path to ogg files.')

args = parser.parse_args()

# Clean up the folder paths.
flac_dir = os.path.abspath(args.flac)
ogg_dir = os.path.abspath(args.ogg)

# Make sure both of these exist and are directories. Raise exception if not.
if not os.path.isdir(flac_dir):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), flac_dir)
if not os.path.isdir(ogg_dir):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), ogg_dir)

for root, dirs, files in os.walk(flac_dir):
    flacs = [f for f in files if f.endswith(FLAC_EXT)]
    arts = [f for f in files if f.endswith(ART_EXT)]

    # Get the directory structure within the flac_dir folder.
    if len(flacs) > 0:
        ogg_out_dir = os.path.join(ogg_dir, os.path.relpath(root, flac_dir))
        if not os.path.isdir(ogg_out_dir):
            os.makedirs(ogg_out_dir)

        # Get any existing ogg files (we will skip these later).
        oggs = [f for f in os.listdir(ogg_out_dir) if f.endswith(OGG_EXT)]

        # Go file by file and see if an ogg already exists. If not,
        # do oggenc.
        for flac_curr in flacs:
            flac_curr_fname, _ = os.path.splitext(flac_curr)
            ogg_curr = os.path.join(ogg_out_dir, flac_curr_fname + OGG_EXT)
            if not os.path.isfile(ogg_curr):
                subprocess.check_call(
                    ('oggenc', '-o', ogg_curr, flac_curr),
                    cwd=root)

        # Check if folder art has been symlinked.
        for art_curr in arts:
            art_full_path = os.path.join(root, art_curr)
            out_art_path = os.path.join(ogg_out_dir, art_curr)
            sym_link_path = os.path.relpath(art_full_path, ogg_out_dir)

            if not os.path.exists(out_art_path):
                os.symlink(sym_link_path, out_art_path)
