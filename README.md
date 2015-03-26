Instance timeout helper
================================

This App Engine application monitors your Google Compute Engine instances and deletes any non-production instances once they're 8 hours old. This helps avoid accidentally running instances for a long time. Any instances tagged "production" will be left running.

> WARNING: When instances are stopped, all data on ephemeral disks is destroyed. This application looks at ALL instances in a project and will delete any instances which aren't tagged "production". For extra safety, the application defaults to running in DRY_RUN mode, where deletes are logged, but not applied. 

This sample application demonstrates the [Compute Engine API](https://developers.google.com/compute/docs/reference/v1beta13/) from App Engine, specifically: listing instances and deleting instances. The same pattern can be used for other GCE API calls.

You can configure how often the application checks the instances, which tags will be left alone and how long instances are allowed to run before deleting them.


## Run Locally

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/), including the [gcloud tool](https://cloud.google.com/sdk/gcloud/), and [gcloud app component](https://cloud.google.com/sdk/gcloud-app).
2. Setup the gcloud tool.

   ```
   gcloud components update app
   gcloud auth login
   gcloud config set project <your-app-id>
   ```
   You don't need a valid app-id to run locally, but will need a valid id to deploy below.
   
1. Clone this repo.

   ```
   git clone https://github.com/GoogleCloudPlatform/compute-appengine-timeout-python.git
   ```
1. Install the required libraries

   ```
   pip install -t lib/ -r requirements.txt
   ```
(Note this requires at least `pip` version 6.0

1. Run this project locally from the command line.

   ```
   gcloud preview app run <REPO NAME>/
   ```

1. Visit the application at [http://localhost:8080](http://localhost:8080).

## Deploying

1. Use the [Cloud Developer Console](https://console.developer.google.com)  to create a project/app id. (App id and project id are identical)
2. Configure gcloud with your app id.

   ```
   gcloud config set project <your-app-id>
   ```
1. Use the [Admin Console](https://appengine.google.com) to view data, queues, and other App Engine specific administration tasks.
1. Use gcloud to deploy your app.

   ```
   gcloud preview app deploy <REPO NAME>/
   ```

1. Congratulations!  Your application is now live at your-app-id.appspot.com

> As long as DRY_RUN is set to `True` (the default) in `main.py`, the application will only log deletes.

View the index at the root of the application, at `http://YOUR-APP-ID.appspot.com`.
Check that production instances are being excluded and older instances would be deleted. 

To create instances tagged "production", add the instance using the GCE Console and include "production" in the tags field. Or add it using gcloud

    $ gcloud compute instances create test --tags production

You can optionally run the cron task manually and check the logs to verify that the correct instances will be deleted. 

Visit `http://YOUR-APP-ID.appspot.com/cron/delete` to run deletes immediately. Then check the AppEngine logs. You should see "DRY_RUN, not deleted" if any instances are old enough to be deleted.

Once everything looks good, edit `main.py` and change `DRY_RUN` to `False`.

Happy Computing!
