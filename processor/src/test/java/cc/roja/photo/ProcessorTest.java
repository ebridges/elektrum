package cc.roja.photo;

import cc.roja.photo.io.ImageLoader;
import cc.roja.photo.io.PhotoProcessorDAO;
import cc.roja.photo.metadata.MetaDataExtractor;
import cc.roja.photo.model.ImageInfo;
import cc.roja.photo.model.ImageKey;
import org.jdbi.v3.core.Handle;
import org.jdbi.v3.core.Jdbi;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.IOException;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class ProcessorTest {
  private Jdbi mockDbi;
  private ImageLoader mockImageLoader;
  private MetaDataExtractor mockMetaDataExtractor;
  private PhotoProcessorDAO mockDao;
  private Handle handle;

  @BeforeEach
  void setup() {
    this.mockDbi = mock(Jdbi.class);
    this.handle = mock(Handle.class);
    this.mockImageLoader = mock(ImageLoader.class);
    this.mockMetaDataExtractor = mock(MetaDataExtractor.class);
    this.mockDao = mock(PhotoProcessorDAO.class);
    when(this.mockDbi.open()).thenReturn(this.handle);
    when(this.handle.attach(PhotoProcessorDAO.class)).thenReturn(mockDao);
  }

  @Test
  void testProcessPhoto_Success() throws IOException {
    Processor underTest = new Processor(this.mockDbi, this.mockImageLoader, this.mockMetaDataExtractor);
    String expectedImageId = "abcd";

    ImageKey mockImageKey = mock(ImageKey.class);
    when(mockImageKey.getKey()).thenReturn("defg");
    File mockFile = mock(File.class);
    ImageInfo imageInfo = new ImageInfo(mockImageKey);

    when(this.mockDao.queryByPath(mockImageKey)).thenReturn(expectedImageId);
    when(this.mockImageLoader.load(mockImageKey.getKey())).thenReturn(mockFile);
    when(this.mockMetaDataExtractor.extract(mockImageKey, mockFile)).thenReturn(imageInfo);

    String actualImageId = underTest.processPhoto(mockImageKey);

    assertEquals(expectedImageId, actualImageId);
  }
}
