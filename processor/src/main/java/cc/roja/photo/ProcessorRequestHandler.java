package cc.roja.photo;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.s3.event.S3EventNotification;

/*
Example event:
```
  {
    "Records":[
      {
        "eventVersion":"2.0",
        "eventSource":"aws:s3",
        "awsRegion":"us-west-2",
        "eventTime":"1970-01-01T00:00:00.000Z",
        "eventName":"ObjectCreated:Put",
        "userIdentity":{
           "principalId":"AIDAJDPLRKLG7UEXAMPLE"
        },
        "requestParameters":{
           "sourceIPAddress":"127.0.0.1"
        },
        "responseElements":{
           "x-amz-request-id":"C3D13FE58DE4C810",
           "x-amz-id-2":"FMyUVURIY8/IgAtTv8xRjskZQpcIZ9KG4V5Wp6S7S/JRWeUWerMUE5JgHvANOjpD"
        },
        "s3":{
           "s3SchemaVersion":"1.0",
           "configurationId":"testConfigRule",
           "bucket":{
              "name":"sourcebucket",
              "ownerIdentity":{
                 "principalId":"A3NL1KOZZKExample"
              },
              "arn":"arn:aws:s3:::sourcebucket"
           },
           "object":{
              "key":"HappyFace.jpg",
              "size":1024,
              "eTag":"d41d8cd98f00b204e9800998ecf8427e",
              "versionId":"096fKKXTRTtl3on89fVO.nfljtsv6qko"
            }
         }
       }
    ]
  }
  ```
 */

public class ProcessorRequestHandler implements RequestHandler<S3EventNotification, ProcessorResult> {
  private Processor processor;

  public ProcessorRequestHandler() {
    this.processor = new Processor();
  }

  @Override
  public ProcessorResult handleRequest(S3EventNotification event, Context context) {
    try {
      ProcessorResult result = new ProcessorResult();
      List<String> imageKeys = new ArrayList<>();

      for(S3EventNotification.S3EventNotificationRecord record : event.getRecords()) {
        S3EventNotification.S3Entity s3Entity = record.getS3();
        imageKeys.add(s3Entity.getObject().getKey());
      }

      for(String imageKey : imageKeys) {
        if (imageKey == null || imageKey.isEmpty()) {
          throw new IllegalArgumentException("missing imageKey");
        }

        String imagePath = imageKey.replace("photos/pictures", "");

        String imageId = processor.processPhoto(imagePath);
        result.addImageId(imageId);
      }

      return result;
    } catch (IOException e) {
      throw new IllegalArgumentException(e);
    }
  }

}
