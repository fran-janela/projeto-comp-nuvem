import os

all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
tf_subdirs = []
for subdir in all_subdirs:
    if subdir.split("-")[0] == "tf":
        tf_subdirs.append(subdir)

def all_created_regions_from_dir(tf_dirs):
    all_created_regions = []
    for tf_dir in tf_dirs:
        all_created_regions.append("-".join(tf_dir.split("-")[1:]))
    return all_created_regions

print(all_created_regions_from_dir(tf_subdirs))