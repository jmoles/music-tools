import argparse
import errno
import os
from shutil import copyfile
import subprocess

FLAC_EXT = ".flac"
ART_EXT = ".jpg"
DEF_OUT_EXT = ".ogg"

OGG_CMD = 'oggenc'

parser = argparse.ArgumentParser(description="Utility to mirror music directory.")
parser.add_argument('flac', help='Base path to flac files.')
parser.add_argument('out', help='Base path to out files.')
parser.add_argument('outExt', help='Output extension.', default=DEF_OUT_EXT)
parser.add_argument('--copy-art', help='Copy art rather than symlink.', action='store_true')

args = parser.parse_args()

out_ext = "." + args.outExt.lstrip(".")

# Clean up the folder paths.
flac_dir = os.path.abspath(args.flac)
ogg_dir = os.path.abspath(args.out)

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
        oggs = [f for f in os.listdir(ogg_out_dir) if f.endswith(out_ext)]

        # Go file by file and see if an ogg already exists. If not,
        # do oggenc.
        for flac_curr in flacs:
            flac_curr_fname, _ = os.path.splitext(flac_curr)
            ogg_curr = os.path.join(ogg_out_dir, flac_curr_fname + out_ext)
            if not os.path.isfile(ogg_curr):
                subprocess.check_call(
                    ('ffmpeg', '-i', flac_curr, ogg_curr),
                    cwd=root)

        # Check if folder art has been symlinked.
        for art_curr in arts:
            art_full_path = os.path.join(root, art_curr)
            out_art_path = os.path.join(ogg_out_dir, art_curr)
            sym_link_path = os.path.relpath(art_full_path, ogg_out_dir)

            if not os.path.exists(out_art_path):
                if args.copy_art:
                    copyfile(sym_link_path, out_art_path)
                else:
                    os.symlink(sym_link_path, out_art_path)

