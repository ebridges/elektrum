## Known Issues & Workarounds

<dl>
<dt>
<strong>
<tt>
<li>
TASK [lam : Link up image processor lambda with media upload bucket.] ********************************************************************************
fatal: [localhost]: FAILED! => {"changed": false, "msg": "An error occurred (InvalidArgument) when calling the PutBucketNotificationConfiguration operation: Unable to validate the following destination configurations"}
</li>
</tt>
</strong>
</dt>
        <dd>
 When linking for the first time the upload bucket in S3 to trigger the upload processor lambda, Ansible generates this error.
        <br>
        <li>
The workaround for this is to use the AWS Console to configure the event notification.  See instructions here:
https://docs.aws.amazon.com/AmazonS3/latest/user-guide/enable-event-notifications.html#enable-event-notifications-how-to
        </li>
        </dd>



<dt>
<strong>
<tt>
<li>
        An error occurred (BadRequestException) when calling the CreateDomainName operation: The domain name you provided already exists.
</li>
<li>
        An error occurred (BadRequestException) when calling the CreateBasePathMapping operation: Invalid REST API identifier specified
</li>
</tt>
</strong>
</dt>
        <dd>
        This may occur if the gateway had been previously created and then deleted.  The root cause is that the A record for your domain name (`${APPLICATION_DOMAIN_NAME}`) does not match the (hidden) Cloudfront distribution that connects the domain name to the API Gateway.
        <br>
        <li>
                As a first step to deal with this, delete the <a href="https://console.aws.amazon.com/apigateway/home?region=us-east-1#/custom-domain-names">Custom Domain Name</a> via the API Gateway admin panel, and then run `undeploy` and then `deploy` to recreate it.
                <br>
                > <i>Note</i>: Creation of the Custom Domain Name associated with the API Gateway takes some time (45-60 minutes) to complete initialization.  Visit the below control panel and look under "ACM Certificate" to track progress of initialization.
                <br>
                <a href="https://console.aws.amazon.com/apigateway/home?region=us-east-1#/custom-domain-names">API Gateway Control Panel</a>
        </li>
        <li>
                To further dig into this, you can check the following:
                <br>
                <blockquote>
                        • In Route 53 go to the hosted zone for ${APPLICATION_DOMAIN_NAME}.  Look for an A record for the bare domain name (i.e. neither static nor <tt>media</tt>).  The Alias Target for that A record should point to a Cloudfront distribution (e.g.: <tt>d2m2kec3ulw33f.cloudfront.net.</tt>).
                        <br>
                        • In Cloudfront, review the existing distributions: there should be two -- one for <tt>media</tt> and one for <tt>static</tt>.  The ID of both of them should <i>not match</i> the ID of the A record's Alias Target.
                        <br>
                        • In API Gateway, review the Custom Domain Name for the endpoint.  It should have a Base Path Mapping that <i>does match</i> the ID of the A record's Alias Target.
                </blockquote>
        </li>
        </dd>
<dt><li><strong><tt>
botocore.errorfactory.NotFoundException: An error occurred (NotFoundException) when calling the GetRestApi operation: Invalid API identifier specified 743873495175:8atzbrhf0a
<br>
botocore.errorfactory.BadRequestException: An error occurred (BadRequestException) when calling the CreateBasePathMapping operation: Invalid REST API identifier specified
</tt>
</strong></li></dt>
        <dd>
        Caused by an API gateway of the same name having been previously deleted.  Solution is to call `undeploy` first and then re-`deploy`.
        </dd>
        <dt><li><strong><tt>TypeError: 'NoneType' object is not callable</tt> when deploying to an environment</strong></li></dt>
        <dd>
        Causes can vary.
        <br>
        Check:
        <li>Ensure host is in `ALLOWED_HOSTS` in the Django configuration.</li>
        </dd>
<dt><li><strong><tt>
ResourceNotFoundException: An error occurred (ResourceNotFoundException) when calling the DescribeLogStreams operation: The specified log group does not exist.</tt></strong></li>
</dt>
        <dd>
        <li>Ensure that API has permissions to log to Cloudwatch.
        <br>
        Add <tt>arn:aws:iam::743873495175:role/elektrum-development-ZappaLambdaExecutionRole</tt> to <kbd>API Gateway / Settings / CloudWatch log role ARN</kbd>
        <br>
        <a href="https://stackoverflow.com/a/50022932/87408">https://stackoverflow.com/a/50022932/87408</a>
        </li>
        </dd>
</dl>

