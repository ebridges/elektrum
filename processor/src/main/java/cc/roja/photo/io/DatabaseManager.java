package cc.roja.photo.io;

import org.postgresql.ds.PGSimpleDataSource;
import org.skife.jdbi.v2.DBI;

@SuppressWarnings("WeakerAccess")
public class DatabaseManager {
  public static DBI getDBI() {
    PGSimpleDataSource dataSource = new PGSimpleDataSource();
    String jdbc_url = System.getenv("DB_JDBC_URL");
    String username = System.getenv("DB_USERNAME");
    String password = System.getenv("DB_PASSWORD");

    dataSource.setUrl(jdbc_url);
    dataSource.setUser(username);
    dataSource.setPassword(password);
    dataSource.setApplicationName("photo-processor");
    //source.setSocketTimeout(); default is "0" which means disable timeout on connection reads

    return new DBI(dataSource);
  }
}
