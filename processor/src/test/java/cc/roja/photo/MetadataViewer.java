package cc.roja.photo;

import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.Comparator;
import java.util.SortedSet;
import java.util.TreeSet;

import com.adobe.xmp.XMPException;
import com.adobe.xmp.XMPIterator;
import com.adobe.xmp.XMPMeta;
import com.adobe.xmp.properties.XMPPropertyInfo;
import com.drew.imaging.ImageMetadataReader;
import com.drew.imaging.ImageProcessingException;
import com.drew.metadata.Directory;
import com.drew.metadata.Metadata;
import com.drew.metadata.Tag;
import com.drew.metadata.xmp.XmpDirectory;

public class MetadataViewer {

  public static void main(String[] args) throws ImageProcessingException, IOException, XMPException {
    String imagePath = args[0];
    File file = new File(imagePath);
    Metadata metadata = ImageMetadataReader.readMetadata(file);

    SortedSet<Directory> directories = new TreeSet<>(new DirectoryComparator());
    metadata.getDirectories().forEach(directories::add);

    for (Directory directory : directories) {
      for (Tag tag : directory.getTags()) {
        System.out.format("[%s - (%s)] - %s (%s / %d) = %s\n",
            directory.getName(), directory.getClass().getSimpleName(), tag.getTagName(), tag.getTagTypeHex(), tag.getTagType(), tag.getDescription());
      }
      if (directory.hasErrors()) {
        for (String error : directory.getErrors()) {
          System.err.format("ERROR: %s\n", error);
        }
      }
    }
    System.out.println("\n===============================================\nMetadata from XMP Directories:\n===============================================");
    Collection<XmpDirectory> xmpDirectories = metadata.getDirectoriesOfType(XmpDirectory.class);
    for (XmpDirectory xmpDirectory : xmpDirectories) {
      XMPMeta xmpMeta = xmpDirectory.getXMPMeta();
      XMPIterator iterator = xmpMeta.iterator();
      while (iterator.hasNext()) {
        XMPPropertyInfo xmpPropertyInfo = (XMPPropertyInfo)iterator.next();
        if(xmpPropertyInfo.getPath() != null) {
          System.out.format("[%s] - %s = %s\n",
              xmpDirectory.getName(), xmpPropertyInfo.getPath(), xmpPropertyInfo.getValue());
        }
      }
    }
  }
}

class DirectoryComparator implements Comparator<Directory> {
  @Override
  public int compare(Directory dir1, Directory dir2) {
    return dir1.getName().compareTo(dir2.getName());
  }
}
