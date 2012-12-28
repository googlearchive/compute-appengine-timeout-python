# In DRY_RUN mode, deletes are only logged. Set this to False after you've
# double-checked the status page and you're ready to enable the deletes.
main_DRY_RUN = True

# Be careful, this application will delete all instances in this project 
# unless they're tagged with one of the SAFE_TAGS below.
main_GCE_PROJECT_ID = 'replace-with-your-compute-engine-project-id'

# Instance tags which will never be deleted.
main_SAFE_TAGS = ['production', 'safetag']

# Instances are deleted after they have been running for TIMEOUT minutes.
main_TIMEOUT = 60 * 8  # in minutes, defaulting to 8 hours
