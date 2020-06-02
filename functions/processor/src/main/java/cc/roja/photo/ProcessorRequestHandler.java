package cc.roja.photo;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import cc.roja.photo.model.ImageKey;
import cc.roja.photo.model.ProcessorResult;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.s3.event.S3EventNotification;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import static java.lang.String.format;

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

@SuppressWarnings("unused")
public class ProcessorRequestHandler implements RequestHandler<S3EventNotification, ProcessorResult> {
  private static final Logger LOG = LogManager.getLogger(ProcessorRequestHandler.class);

  @Override
  public ProcessorResult handleRequest(S3EventNotification event, Context context) {
    try {
      Processor processor = new Processor();
      ProcessorResult result = new ProcessorResult();
      Map<String, String> objectKeys = new HashMap<>();

      for(S3EventNotification.S3EventNotificationRecord record : event.getRecords()) {
        S3EventNotification.S3Entity s3Entity = record.getS3();
        objectKeys.put(s3Entity.getObject().getKey(), record.getEventName());
      }

      LOG.info("Processing "+objectKeys.size()+"event records.");
      for(String objectKey : objectKeys.keySet()) {
        if (objectKey == null || objectKey.isEmpty()) {
          continue;
        }

        String imagePath = objectKey.replace("photos/pictures", "");
        ImageKey imageKey = ImageKey.parse(imagePath);

        String eventName = objectKeys.get(objectKey);

        String imageId = null;
        if(eventName.contains("Created")) {
          LOG.info("processing image: " + imageKey);
          imageId = processor.processPhoto(imageKey);
        } else if(eventName.contains("Removed")) {
          LOG.info("removing image: " + imageKey);
          imageId = processor.removePhoto(imageKey);
        }
        result.addImageId(imageId);
        LOG.info("> Processed image "+imageKey+" ["+imageId+"]");
      }

      if(objectKeys.size() != result.count()) {
        LOG.warn(format("result count did not match event count: [%d vs. %d]", result.count(), objectKeys.size()));
      }

      return result;
    } catch (IOException e) {
      LOG.error(format("Caught IOException: %s", e.getMessage()), e);
      throw new IllegalArgumentException(e);
    }
  }
}
