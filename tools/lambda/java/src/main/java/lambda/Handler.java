package lambda;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.s3.event.S3EventNotification;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

public class Handler implements RequestHandler<S3EventNotification, String> {
  private static final Logger LOG = LogManager.getLogger(Handler.class);

  @Override
  public String handleRequest(S3EventNotification event, Context context) {
    System.out.println("\n\nBEGIN");
    LOG.traceEntry();
    LOG.debug("hello: debug");
    LOG.info("hello: info");
    LOG.warn("hello: warning");
    LOG.error("hello: error");
    LOG.traceExit("exiting logging");
    return "Lambda Successfully Executed";
  }
}
