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
import org.jdbi.v3.core.Handle;
import org.jdbi.v3.core.Jdbi;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class Processor {
  private static final Logger LOG = LogManager.getLogger(Processor.class);

  private Jdbi dbi;
  private ImageLoader imageLoader;
  private MetaDataExtractor metaDataExtractor;

  Processor(Jdbi dbi, ImageLoader imageLoader, MetaDataExtractor metaDataExtractor) {
    this.dbi = dbi;
    this.imageLoader = imageLoader;
    this.metaDataExtractor = metaDataExtractor;
  }

  Processor() {
    this(DatabaseManager.getDBI(), ImageLoaderFactory.getLoader(), new MetaDataExtractor());
  }

  public String removePhoto(ImageKey imageKey) throws IOException {
    try (Handle handle = dbi.open()) {
      PhotoProcessorDAO dao = handle.attach(PhotoProcessorDAO.class);
      LOG.info("Deleting: " + imageKey);
      dao.deleteImage(imageKey);
      return imageKey.getImageId().toString();
    }
  }

  public String processPhoto(ImageKey imageKey) throws IOException {
    try (Handle handle = dbi.open()) {
      PhotoProcessorDAO dao = handle.attach(PhotoProcessorDAO.class);

      LOG.info("Processing: " + imageKey);

      // identify a filesystem location for the media item, which will mean a network op for S3
      File imageFile = imageLoader.load(imageKey.getKey());

      // extract and normalize metadata from the media file
      ImageInfo imageInfo = metaDataExtractor.extract(imageKey, imageFile);

      // store the metadata linked to the media id record
      Integer count = dao.insertImage(imageInfo);

      if(count != 1) {
        LOG.warn("Image at path [{}] could not be updated.", imageKey.getKey());
      }

      return imageKey.getImageId().toString();
    }
  }
}