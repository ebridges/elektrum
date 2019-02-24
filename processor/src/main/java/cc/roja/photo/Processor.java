package cc.roja.photo;

import java.io.File;
import java.io.IOException;

import cc.roja.photo.io.DatabaseManager;
import cc.roja.photo.io.ImageLoader;
import cc.roja.photo.io.ImageLoaderFactory;
import cc.roja.photo.io.PhotoProcessorDAO;
import cc.roja.photo.metadata.MetaDataExtractor;
import cc.roja.photo.model.ImageInfo;
import cc.roja.photo.model.ImageKey;
import org.skife.jdbi.v2.DBI;

import org.apache.log4j.Logger;

import static java.lang.String.format;

@SuppressWarnings({"unused","WeakerAccess"})
public class Processor {
  private static final Logger LOG = Logger.getLogger(Processor.class);

  private DBI dbi;
  private ImageLoader imageLoader;

  public Processor(DBI dbi, ImageLoader imageLoader) {
    this.dbi = dbi;
    this.imageLoader = imageLoader;
  }

  public Processor() {
    this.dbi = DatabaseManager.getDBI();
    this.imageLoader = ImageLoaderFactory.getLoader();
  }

  public String processPhoto(String imageIdentifier) throws IOException {
    if(imageIdentifier == null || imageIdentifier.isEmpty()) {
      throw new IllegalArgumentException("image identifier cannot be null/empty");
    }

    ImageKey imageKey = new ImageKey();
    imageKey.parse(imageIdentifier);

    try (PhotoProcessorDAO dao = dbi.open(PhotoProcessorDAO.class)) {
      String imageId = dao.queryByPath(imageKey);

      if(imageId == null) {
        LOG.warn(format("No image record found for: [%s]", imageKey));
        throw new IllegalArgumentException(format("No image record found for: [%s]", imageKey));
      }

      LOG.info("Processing: " + imageKey);
      ImageInfo imageInfo = new ImageInfo(imageKey.getFilePath());

      // identify a filesystem location for the media item, which will mean a network op for S3
      File imageFile = imageLoader.load(imageKey.getKey());

      // extract and normalize metadata from the media file
      MetaDataExtractor metaDataExtractor = new MetaDataExtractor();
      metaDataExtractor.extract(imageFile, imageInfo);

      // store the metadata linked to the media id record
      return dao.updateImageInfo(imageId, imageInfo);
    }
  }
}
