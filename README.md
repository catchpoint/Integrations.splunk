### Catchpoint Integration for Splunk Documentation ###

#### Developer's Note  ####
Open-Source Software libraries used within this add-on include:

* Oauth2 version 1.5
* Httplib2 version 0.8
* Requests version 2.2.1
* SplunkLib version 1.6.14

#### Support ####

For technical support, questions or concerns on the release --
contact our development team at support@catchpoint.com.

---------------------------------------

#### Installation and Initial Setup ####


Technical Note

_app.conf overview:_ `$SPLUNK_HOME/Splunk/etc/apps/search_cp/local/app.conf`

Upon initial setup, the parameter `is configured` located under the stanza `install` must have a value of `0`. This value represents that the application is indeed starting up for the first time and is not configured for use. A user's first use of the Catchpoint Splunk Modular Input should, by default, take the user to the `App configuration` page when the `is configured` is 0.

---------------------------------------

From the home view of SplunkWeb, navigate to the left-hand side and select the grayed `Find More Apps` icon. In the search bar that appears, search for `Catchpoint Search` and select `Install`. Upon completion, select  `Restart`. Once restarted, from the home view, select the `Catchpoint Search` app found on the left-hand side of the view. On the `App configuration` page which follows, select `Continue to app page setup` to continue.

On the setup page, the base URL (Catchpoint API URL) has been automatically set.
Complete the setup by supplying the consumer key and consumer secret within the remaining fields.

Multiple client/division support for performance and alerts data:
1. To pull data from multiple client/division, Navigate to `Manage Apps` page.
1. Search for `Catchpoint Search` and select `Set up` from Actions.
1. Complete the setup by supplying the consumer key and consumer secret within the remaining fields.

---------------------------------------

#### Manual Installation ####

If manually installing the application from its tarball form, it is important to ensure (when the .tar has been expanded) that the base directory's name of the application is `search_cp`.

The end result of a manual installation should reflect the following folder structure -- where search_cp is the name of the application directory.

~SPLUNK_HOME

    \etc

    ..\apps

    ..\..\search_cp



---------------------------------------

#### Getting Data In ####
Navigate to Settings > Data inputs and locate Catchpoint Modular Input. On the right-hand side of the located row, select `Add New`. To begin ingesting Catchpoint data within Splunk, supply the required values for `Catchpoint Input Name`, `Test ID` and `Client Secret`, `Catchpoint Input Name` is used only for labeling the tests json. `Client Secret` should match one of the consumer secret key which was supplied in the set up page.

It should be noted that the user should pay special attention to the required format of the `Test ID` field.
The modular input can be setup with just one test ID, however, if the user chooses to create the modular input with multiple test IDs,
it is required multiple test IDs

* be of a comma-seperated values form.
* be of the same test type.


Example.

Assume the following Test IDs to be of the same type:

* XXX
* YYY
* ZZZ

Assume the following Test ID to be of a different type of the IDs mentioned above:

* BBB

As an example,
```sh
https://io.catchpoint.com/v{version}/performance/raw?tests=XXX,YYY,ZZZ
```

is a __VALID endpoint__ because

* the Test IDs provided are of a comma-seperated values form.
* the Test IDs provided are of the same test type.

As a closing example,
```sh
    https://io.catchpoint.com/v{version}/performance/raw?tests=XXX,BBB,YYY
```
is an __INVALID endpoint__ because although

* the Test IDs provided are of a comma-seperated values form,
* the Test IDs provided are NOT of the same test type.

Options

Under `More settings`, the user is able to set the `Index` and `Host` field values.
The `Index` dropdown sets the destination index for this source. It is recommended users choose `catchpoint` as the specified index. To finish input setup, select `Next` toward the top of the page's view.


Closing Note

The frequency or 'interval' of how often the newly created data input is executed has been programmatically determined by using the start and end time values of the initial event json recently indexed into Splunk.

---------------------------------------

#### Viewing the Data Within Splunk ####

Upon completing the `Getting Data In` section, the user is now ready to view thier data being ingested within Splunk. From Splunk's homepage, select the `Catchpoint Search` app icon found on the left-hand side.

The user is able to complete searches within the Catchpoint index with the command `index = catchpoint `.
