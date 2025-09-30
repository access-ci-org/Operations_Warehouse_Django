#!/bin/bash
###############################################################################
#
# Get opsapi django  backups from AWS s3
# Author: Eric Blau, 2023-10-29
# based on retrieve_s3.sh by
# Author: JP Navarro, 2023-03-13
#
#   # Place the following in your ~/.aws/config
#     [profile newbackup]
#     region = us-east-2
#     output = json
#     aws_access_key_id = <GET VALUE FROM SOMEONE>
#     aws_secret_access_key = <GE VALUE FROM SOMEONE>
#
# Usage: ./get_django_backup.sh [-l] [<hostname>:]<pattern>
#
# Exammples:
#      # List all django backups
#      $ ./get_django_backup.sh -l 
#
#      # List backups matching a (partial) epoch string
#      $ ./get_django_backup.sh -l django.dump.1701291601
#
#      # Retrieve to the dbrestore/ directory all backups matching a date and time string
#      $ ./get_django_backup.sh    django.dump.1701291601
#
#      # Retrieve to the dbrestore/ directory the most recent django.dump
#      $ ./get_django_backup.sh    
#
###############################################################################

if [ ! -f "/opt/app/aws_credentials_local" ]
then
    echo "No aws_credentials_local file found.  Please run local_scripts/decrypt_credentials.sh"
    exit
fi
ME=$(basename "$0" .sh)
DATE=`date +'%s'`
MY_HOSTNAME=`hostname -f`
APP_BASE="./"
RESTORE_DIR="${APP_BASE}/dbrestore"

# Process arguments
if [ "$1" = "-l" ]; then
        MODE='list'
        FILTER=$2
else
        MODE='retrieve'
        FILTER=$1
fi
arrFILTER=(${FILTER//:/ })
if [[ "$FILTER" == *":"* ]]; then
        HOSTNAME=${arrFILTER[0]}
        PATTERN=${arrFILTER[1]}
else
        HOSTNAME=$MY_HOSTNAME
        PATTERN=${arrFILTER[0]}
fi

S3_BUCKET="s3://backup.operations.access-ci.org/operations-api.access-ci.org/rds.backup/"

###############################################################################
# Do stuff

LOG=${APP_BASE}/var/${ME}.log
exec 1>> ${LOG}
echo ${ME} Start at `date +'%F_%T'`
echo ${ME} Remote bucket = ${S3_BUCKET}

#find the most recent backup by doing an aws s3 ls and sorting the output
#since filenames are the same aside from unix epoch, the last one is most recent
IFS=$'\n' read -r -d '' -a my_array < <( aws s3 ls ${S3_BUCKET} --profile newbackup | awk 'BEGIN{ORS="\n"}{print $4}' |sort -z )

length=${#my_array[@]}
echo $length
echo "last index is " ${my_array[$length-1]}
match_array=()
for filename in "${my_array[@]}"
do
    # Ignore anything that doesn't match the pattern
    if [[ ! -z "$PATTERN" && "${filename}" != *"$PATTERN"* ]]; then
                continue
    else
        # Everything here matches the pattern
        if [[ ! -z "$PATTERN" ]]; then
          match_array+=(${filename})
        fi
   fi
done
echo "matcharray is ${match_array[*]}" >&2

match_length=${#match_array[@]}
for filename in "${match_array[@]}"
do
    if [[ ! -z "$PATTERN" && "${filename}" != *"$PATTERN"* ]]; then
                continue
        fi
    if [ "$MODE" = "list" ]; then
        echo "Found -> ${S3_BUCKET}${filename}" >&2
    fi
done

# Function to decompress and handle errors
decompress_backup() {
    local filename=$1
    echo "Decompressing ${filename}..." >&2
    cd ${RESTORE_DIR}
    if gzip -d --stdout ${filename} > django.dump.latest; then
        echo "Successfully decompressed to django.dump.latest" >&2
        ls -la django.dump.latest >&2
    else
        echo "ERROR: Failed to decompress ${filename}" >&2
        return 1
    fi
}

#Download only the most recent matching pattern
if [[ ! -z "$PATTERN" && "$MODE" != "list" ]]; then
   echo "Retrieved -> ${RESTORE_DIR}/${match_array[$match_length-1]}" >&2
   aws s3 cp ${S3_BUCKET}${match_array[$match_length-1]} ${RESTORE_DIR}/${match_array[$match_length-1]} --profile newbackup
   decompress_backup ${match_array[$match_length-1]}
fi

#If no pattern was given, only download the most recent
if [[ -z "$PATTERN" && "$MODE" != "list" ]]; then
   echo "Retrieved -> ${RESTORE_DIR}/${my_array[$length-1]}" >&2
   aws s3 cp ${S3_BUCKET}${my_array[$length-1]} ${RESTORE_DIR}/${my_array[$length-1]} --profile newbackup
   decompress_backup ${my_array[$length-1]}
fi

echo ${ME} Done at `date +'%F_%T'`