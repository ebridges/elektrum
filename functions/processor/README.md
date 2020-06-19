### Setup

#### Environment variables:

##### Database

* `DB_USERNAME`
* `DB_PASSWORD`
* `DB_JDBC_URL`

    JDBC URL Format:
    `jdbc:postgresql://${hostname}:${port_num}/${database}`

##### Filesystem

When loading images from S3 use set `BUCKET_NAME`.  When loading files from local disk use `IMAGE_ROOT`.


https://stackoverflow.com/questions/37415469/how-we-can-use-jdbc-connection-pooling-with-aws-lambda

##### Clean-Up

When the image is missing `DateTimeOriginal`

Search: `(\d{4}/\d{4}-\d{2}-\d{2}/)(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})(_\d{2}\.jpg)`

Replace: `exiftool '-datetimeoriginal=$2:$3:$4 $5:$6:$7' $1$2$3$4T$5$6$7$8 && exiftool '-gpstimestamp<${datetimeoriginal}-05:00' '-gpsdatestamp<${datetimeoriginal}-05:00' $1$2$3$4T$5$6$7$8`
