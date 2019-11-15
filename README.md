AWS Onboarding tool for Prisma Cloud

Simple one-liner tool to add account to Prisma Cloud

May use export.sh for environment variables or lambda 

Or use available commandline arguments
```
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Prisma Cloud username or access key id
  -p PASSWORD, --password PASSWORD
                        Prisma Cloud password or secret key
  -c CUSTOMERNAME, --customername CUSTOMERNAME
                        Prisma Cloud tenant name
  -a ACCOUNTNAME, --accountname ACCOUNTNAME
                        Account name to be used for AWS account within Prisma
                        Cloud
  -g ACCOUNTGROUP, --accountgroup ACCOUNTGROUP
                        Prisma Cloud account group to assign to this account
  -e EXTERNALID, --externalid EXTERNALID
                        External ID that is configured for the AWS account
                        trust relationship
  -r ROLENAME, --rolename ROLENAME
                        Name of the role added for Prisma Cloud access eg,
                        PrismaReadOnlyRole
  -t TENANT, --tenant TENANT
                        select Prisma Cloud tenant (app, app2, app3, app4,
                        app.eu, app.anz, app.gov
  -n, --updateacct      This flag will cause an existing account to be updated
                        rather than created

Example

-u some@email.com -p foo -c Widgets Inc -a Widget Prod -g "Default Account Group" -e AWSEXTERNALID -r PrismaReadOnlyRole --tenant app
```
