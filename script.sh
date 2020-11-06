#### developer's notes ####
#### permissions script ####
#### as per splunk, recommended permissions ####
#### run this before each release ####

#### on win envirorments: ####
#### !IMPORTANT: run this cmd in the folder where the `splunk` directory exists ####
#### clears caridge return characters ####
#### sed -i 's/\r//g' splunk/script.sh ####

#### !IMPORTANT: run this cmd in the folder where the `splunk` directory exists ####
#### bash splunk/script.sh ####


#!/bin/bash
rm -rf deliverable
mkdir deliverable
cp -R splunk deliverable
mv deliverable/splunk deliverable/search_cp
cd deliverable/search_cp/bin
rm -rf test
cd ..
###Added By Osho 24-Mar-2017
## as per splunk specifications
### there should be no hidden files or compiled files within the package hence removing them
find . -iname ".*" -maxdepth 100 -type f -delete ####removing hidden files
find . -iname "*.pyo" -maxdepth 100 -type f -delete ####removing all pyo files
find . -iname "*.pyc" -maxdepth 100 -type f -delete #### removing all pyc file
#### removing local folder
rm -rf local/
#### removing local.meta from metadata
rm -rf metadata/local.meta
#### Check that all files not in the /bin directory do not have *nix execute permissions. Splunk recommends 644 for all files
#### outside of bin/ and 755 for all directories and files in the bin/ directory.
chmod 777 * -R ###done 777 because all checks were failing
#chmod 755 bin/ -R


echo "standardizing directory from development -> release.."
for i in $(ls -a); do
  #### the five required directories within of the application ####
  if [[ !(-d "$i" && !("$i" = .*)) && !("$i" = "RELEASE_NOTES.md")  && !( "$i" = "README.md") ]]; then
    printf %s"\n\nREMOVING FILE: $i\n"
    rm -rf  "$i"
  fi
done

printf %s"\n\nsearch_cp\n"
ls -al
cd ..
#chmod -R 755 search_cp
ls -al search_cp
tar -cvpzf search_cp.tar.gz search_cp
ls -al
rm -rf search_cp 
# mv search_cp.tar.gz search_cp.spl

#### end script ####

# #### untar ####
# tar xpvzf search_cp.tar.gz
# ls -l search_cp/default
# ls -l search_cp/metadata
# ls -l search_cp/README
# ls -l search_cp/static
# # cd search_cp
# # ls -l
# # cd ..
# # rm -rf search_cp.tar.gz
# # rm -rf search_cp
# #### done. ####
