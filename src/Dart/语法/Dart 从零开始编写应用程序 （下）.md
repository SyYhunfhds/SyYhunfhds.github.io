---
title: Dart 从零开始编写应用程序 （下）
date: 2026-05-02
---
[[toc]]
***
## 测试你的程序和代码 Test your app & code
> In this chapter, you will add tests to the `wikipedia` package, ensuring that the JSON deserialization logic for your data models is working correctly.

### 增加`test`依赖 Add the test dependency
> First, you need to confirm that the `test` package is already a development dependency in your project.
> 1. Open the `wikipedia/pubspec.yaml` file within your project.
> 2. Locate the `dev_dependencies` section.
> 3. Verify that `test: ^1.24.0` (or the latest stable version) is present under `dev_dependencies`.
```yaml
dev_dependencies:
  lints: ^5.0.0
  test: ^1.24.0

```
> If the `test` dependency is missing, add it to your `pubspec.yaml` file. The `^` symbol allows compatible versions to be used.

> 4. If you made any changes to the file, save `pubspec.yaml` and run `dart pub get` in your terminal from the `wikipedia` directory. This command fetches any newly added dependencies and makes them available for use in your project.
> You should see output similar to this:
```bash
Resolving dependencies...
Downloading packages...
+ test 1.25.1
Changed 2 dependencies!

```

### 创建一个测试文件并添加导入语句 Create a test file and add imports
> Next, create a test file for your data models and add the necessary imports to it.
> 1. Navigate to the `wikipedia/test` directory.
> 2. Create a new file named `model_test.dart` in this directory.
> 3. Open the `wikipedia/test/model_test.dart` file and add the following `import` statements at the top of the file:
```dart
import 'dart:convert';
import 'dart:io';

import 'package:test/test.dart';
import 'package:wikipedia/src/model/article.dart';
import 'package:wikipedia/src/model/search_results.dart';
import 'package:wikipedia/src/model/summary.dart';

const String dartLangSummaryJson = './test/test_data/dart_lang_summary.json';
const String catExtractJson = './test/test_data/cat_extract.json';
const String openSearchResponse = './test/test_data/open_search_response.json';

```
> These lines import the `test` package, which provides the testing framework and the data model files you want to test. The constant strings declare the location of your sample data.

### 创建测试数据文件 Create the test data files
> The tests you need to write rely on local JSON files that mimic the responses from the Wikipedia API. You need to create a `test_data` directory and populate it with three files.
> 1. Navigate to the `wikipedia/test` directory.
> 2. Create a new directory named `test_data`.
> 3. Inside the `test_data` directory, create a new file named `dart_lang_summary.json` and paste the following content into it:

```json
{
  "type": "standard",
  "title": "Dart (programming language)",
  "displaytitle": "<span class=\"mw-page-title-main\">Dart (programming language)</span>",
  "namespace": {
      "id": 0,
      "text": ""
  },
  "wikibase_item": "Q406009",
  "titles": {
    "canonical": "Dart_(programming_language)",
    "normalized": "Dart (programming language)",
    "display": "<span class=\"mw-page-title-main\">Dart (programming language)</span>"
  },
  "pageid": 33033735,
  "lang": "en",
  "dir": "ltr",
  "revision": "1259309990",
  "tid": "671bc7c6-aa67-11ef-aa2a-7c1da4fbe8fb",
  "timestamp": "2024-11-24T13:24:16Z",
  "description": "Programming language",
  "description_source": "local",
  "content_urls": {
    "desktop": {
      "page": "https://en.wikipedia.org/wiki/Dart_(programming_language)",
      "revisions": "https://en.wikipedia.org/wiki/Dart_(programming_language)?action=history",
      "edit": "https://en.wikipedia.org/wiki/Dart_(programming_language)?action=edit",
      "talk": "https://en.wikipedia.org/wiki/Talk:Dart_(programming_language)"
    },
    "mobile": {
      "page": "https://en.m.wikipedia.org/wiki/Dart_(programming_language)",
      "revisions": "https://en.m.wikipedia.org/wiki/Special:History/Dart_(programming_language)",
      "edit": "https://en.m.wikipedia.org/wiki/Dart_(programming_language)?action=edit",
      "talk": "https://en.m.wikipedia.org/wiki/Talk:Dart_(programming_language)"
    }
  },
  "extract": "Dart is a programming language designed by Lars Bak and Kasper Lund and developed by Google. It can be used to develop web and mobile apps as well as server and desktop applications.",
  "extract_html": "<p><b>Dart</b> is a programming language designed by Lars Bak and Kasper Lund and developed by Google. It can be used to develop web and mobile apps as well as server and desktop applications.</p>"
}

```

> 4. Next, create a file named `cat_extract.json`. This file is very long, so copy the contents from this link: https://github.com/ericwindmill/dash_getting_started/blob/main/dart_step_by_step/step_10/wikipedia/test/test_data/cat_extract.json

> 5.Next, create a file named `open_search_response.json` and paste this content into it:
```json
[
    "dart",
    [
        "Dart",
        "Darth Vader",
        "Dartmouth College",
        "Darts",
        "Darth Maul",
        "Dartford Crossing",
        "Dart (programming language)",
        "Dartmouth College fraternities and sororities",
        "Dartmoor",
        "Dartmouth, Massachusetts"
    ],
    [
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ],
    [
        "https://en.wikipedia.org/wiki/Dart",
        "https://en.wikipedia.org/wiki/Darth_Vader",
        "https://en.wikipedia.org/wiki/Dartmouth_College",
        "https://en.wikipedia.org/wiki/Darts",
        "https://en.wikipedia.org/wiki/Darth_Maul",
        "https://en.wikipedia.org/wiki/Dartford_Crossing",
        "https://en.wikipedia.org/wiki/Dart_(programming_language)",
        "https://en.wikipedia.org/wiki/Dartmouth_College_fraternities_and_sororities",
        "https://en.wikipedia.org/wiki/Dartmoor",
        "https://en.wikipedia.org/wiki/Dartmouth,_Massachusetts"
    ]
]

```
> With these files in place, you're ready to write the tests that will verify your data models.

### 为JSON反序列化编写测试 Write tests for JSON deserialization
> Now, you'll write tests for the JSON deserialization logic in your data models. You'll use the `group`, `test`, and `expect` functions from the `test` package.
> 1. Use the `group` function to group related tests together. Add the following to your `wikipedia/test/model_test.dart` file:
```dart
void main() {
  group('deserialize example JSON responses from wikipedia API', () {
    // Tests will go here
  });
}

```
> The `group` function takes a description of the group and a callback function that contains the tests.

> 2. Create a test for the `Summary` model. Add the following `test` function inside the `group` function:
```dart
void main() {
  group('deserialize example JSON responses from wikipedia API', () {
    test('deserialize Dart Programming Language page summary example data from '
        'json file into a Summary object', () async {
      final String pageSummaryInput =
          await File(dartLangSummaryJson).readAsString();
      final Map<String, Object?> pageSummaryMap =
          jsonDecode(pageSummaryInput) as Map<String, Object?>;
      final Summary summary = Summary.fromJson(pageSummaryMap);
      expect(summary.titles.canonical, 'Dart_(programming_language)');
    });
  });
}

```
> This `test` function does the following:
- Reads the contents of the `dart_lang_summary.json` file.
- Decodes the JSON string into a `Map<String, Object?>`.
- Creates a `Summary` object from the map using the `Summary.fromJson` constructor.
- Uses the `expect` function to assert that the `canonical` property of the `titles` object is equal to `'Dart_(programming_language)'`.
> The `expect` function takes a value and a matcher. The matcher is used to assert that the value meets certain criteria. In this case, the `equals` matcher is used to assert that the value is equal to a specific string.

> 3. Create a test for the `Article` model. Add the following `test` function inside the `group` function, after the previous test:
```dart
void main() {
  group('deserialize example JSON responses from wikipedia API', () {
    test('deserialize Dart Programming Language page summary example data from '
        'json file into a Summary object', () async {
      final String pageSummaryInput =
          await File(dartLangSummaryJson).readAsString();
      final Map<String, Object?> pageSummaryMap =
          jsonDecode(pageSummaryInput) as Map<String, Object?>;
      final Summary summary = Summary.fromJson(pageSummaryMap);
      expect(summary.titles.canonical, 'Dart_(programming_language)');
    });

    test('deserialize Cat article example data from json file into '
        'an Article object', () async {
      final String articleJson = await File(catExtractJson).readAsString();
      final Map<String, Object?> articleMap =
          jsonDecode(articleJson) as Map<String, Object?>;
      final List<Article> articles = Article.listFromJson(articleMap);
      expect(articles.first.title.toLowerCase(), 'cat');
    });
  });
}

```
> This `test` function does the following:
- Reads the contents of the `cat_extract.json` file.
- Decodes the JSON string into a `Map<String, Object?>`.
- Creates the `List<Article>` object from the map using the `Article.listFromJson` static method.
- Uses the `expect` function to assert that the `title` property of the first article is equal to `'cat'`.

> 4. Create a test for the `SearchResults` model. Add the following `test` function inside the `group` function, after the previous test:
```dart
void main() {
  group('deserialize example JSON responses from wikipedia API', () {
    test('deserialize Dart Programming Language page summary example data from '
          'json file into a Summary object', () async {
      final String pageSummaryInput =
          await File(dartLangSummaryJson).readAsString();
      final Map<String, Object?> pageSummaryMap =
          jsonDecode(pageSummaryInput) as Map<String, Object?>;
      final Summary summary = Summary.fromJson(pageSummaryMap);
      expect(summary.titles.canonical, 'Dart_(programming_language)');
    });

    test('deserialize Cat article example data from json file into '
        'an Article object', () async {
      final String articleJson = await File(catExtractJson).readAsString();
      final Map<String, Object?> articleMap =
          jsonDecode(articleJson) as Map<String, Object?>;
      final List<Article> articles = Article.listFromJson(articleMap);
      expect(articles.first.title.toLowerCase(), 'cat');
    });

    test('deserialize Open Search results example data from json file '
        'into an SearchResults object', () async {
      final String resultsString =
          await File(openSearchResponse).readAsString();
      final List<Object?> resultsAsList =
          jsonDecode(resultsString) as List<Object?>;
      final SearchResults results = SearchResults.fromJson(resultsAsList);
      expect(results.results.length, greaterThan(1));
    });
  });
}

```
> This `test` function does the following:
- Reads the contents of the `open_search_response.json` file.
- Decodes the JSON string into a `List<Object?>`.
- Creates a `SearchResults` object from the list using the `SearchResults.fromJson` constructor.
- Uses the `expect` function to assert that the `results` list has a length greater than `1`.

### 运行测试 Run the tests
> Now that you've written the tests, you can run them to verify that they pass.
> 1. Open your terminal and navigate to the `wikipedia` directory.
> 2. Run the command `dart test`.
> 	You should see output similar to this:
```bash
00:02 +4: All tests passed!
```
> 	This confirms that all three tests are passing.

![](assets/Pasted%20image%2020260502235004.png)

### 课后练习
#### `group`、`test`和`expect`的关系是什么
> **What's the relationship between `group`, `test`, and `expect` in Dart's testing library?**
```Markdown
`group` organizes related tests, `test` defines individual test cases, `expect` asserts that values match expectations.
```
> Groups contain tests, tests contain expectations. This hierarchy keeps your test suite organized and your assertions clear.

#### `greaterThan`函数的作用是什么
> **In `expect(results.length, greaterThan(1))`, what is `greaterThan(1)` called and what does it do?**
```Markdown
A matcher. It describes the condition the actual value should satisfy.
```
> Matchers like `greaterThan`, `equals`, `contains`, and `isNull` describe expected conditions. They make test assertions readable and provide helpful failure messages.

#### 在`await`了一个异步函数之后，你应该对测试函数做些什么以便让它跑起来
> **You write a test that calls `await File(path).readAsString()`. What do you need to add to the test function for this to work?**
```Markdown
Mark the test callback as `async`: `test('...', () async { ... })`
```
> Just like regular Dart functions, test callbacks can be `async`. The test framework automatically waits for the returned `Future` to complete.

## 简单爬虫 Fetch data from the internet
> In this chapter, you'll move beyond simple scripts and implement a proper API layer. You'll work within the `wikipedia` package to implement the API client logic, which improves your application's scalability and maintainability.

### 给`wikipedia`包加上`http`依赖 Add the http dependency to the wikipedia package
> To make HTTP requests, you need to add the `http` package as a dependency to the `wikipedia` package.
> 1. Open the `wikipedia/pubspec.yaml` file within your project.
> 2. Locate the `dependencies` section.
> 3. Add `http: ^1.3.0` (or the latest stable version) under `dependencies`.
```yaml
dependencies:
  http: ^1.6.0 # 现在最新是1.6.0

```
4. Save the `pubspec.yaml` file.
5. Run `dart pub get` in your terminal from the `wikipedia` directory.

也可以直接：
```bash
dart pub add http
```
这会自动在`pubspec.yaml`里加上导入语句，并隐式运行`dart pub get`：
```yaml
dependencies:
  http: ^1.6.0
```
:::note Dart SDK版本与`pub.dev`元数据不一致
```bash
╰─ dart pub get
Resolving dependencies in `F:\DartProjects\dartpedia`...
Downloading packages...
Failed to decode advisories for http from https://pub.dev.
FormatException: advisoriesUpdated must be a String
package:pub/src/source/hosted.dart 670               HostedSource._extractAdvisoryDetailsForPackage
package:pub/src/source/hosted.dart 622               HostedSource._fetchAdvisories
===== asynchronous gap ===========================
```

练习时Dart SDK版本为3.11.5，待下载的http依赖版本为1.6.0。报错原因不明
:::


### 实现`wikipedia`API调用 Implement Wikipedia APi Calls
> Next, you'll create the API functions to fetch data from Wikipedia. You'll create three files:
> - `summary.dart`: This file will contain functions for retrieving article summaries.
> - `search.dart`: This file will handle search queries to find articles.
> - `get_article.dart`: This file will contain functions for fetching the full content of an article.

> 1. Create the directory `wikipedia/lib/src/api`.
> 2. Create the file `wikipedia/lib/src/api/summary.dart`.
> 3. Add the following code to `wikipedia/lib/src/api/summary.dart`:

```dart
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../model/summary.dart';

Future<Summary> getRandomArticleSummary() async {
  final http.Client client = http.Client();
  try {
    final Uri url = Uri.https(
      'en.wikipedia.org',
      '/api/rest_v1/page/random/summary',
    );
    final http.Response response = await client.get(url);
    if (response.statusCode == 200) {
      final Map<String, Object?> jsonData =
          jsonDecode(response.body) as Map<String, Object?>;
      return Summary.fromJson(jsonData);
    } else {
      throw HttpException(
        '[WikipediaDart.getRandomArticle] '
        'statusCode=${response.statusCode}, body=${response.body}',
      );
    }
  } on FormatException {
    // todo: log exceptions
    rethrow;
  } finally {
    client.close();
  }
}

Future<Summary> getArticleSummaryByTitle(String articleTitle) async {
  final http.Client client = http.Client();
  try {
    final Uri url = Uri.https(
      'en.wikipedia.org',
      '/api/rest_v1/page/summary/$articleTitle',
    );
    final http.Response response = await client.get(url);
    if (response.statusCode == 200) {
      final Map<String, Object?> jsonData =
          jsonDecode(response.body) as Map<String, Object?>;
      return Summary.fromJson(jsonData);
    } else {
      throw HttpException(
        '[WikipediaDart.getArticleSummary] '
        'statusCode=${response.statusCode}, body=${response.body}',
      );
    }
  } on FormatException {
    // todo: log exceptions
    rethrow;
  } finally {
    client.close();
  }
}

```
> This code defines two functions: `getRandomArticleSummary` and `getArticleSummaryByTitle`. Both functions use the `http` package to make GET requests to the Wikipedia API and return a `Summary` object. `getRandomArticleSummary` fetches a summary for a random article, while `getArticleSummaryByTitle` fetches a summary for a specific article title.

> 4. Next create the file `wikipedia/lib/src/api/search.dart`.
> 5. Add the following code to `wikipedia/lib/src/api/search.dart`:

```dart

import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../model/search_results.dart';

Future<SearchResults> search(String searchTerm) async {
  final http.Client client = http.Client();
  try {
    final Uri url = Uri.https(
      'en.wikipedia.org',
      '/w/api.php',
      <String, Object?>{
        'action': 'opensearch',
        'format': 'json',
        'search': searchTerm,
      },
    );
    final http.Response response = await client.get(url);
    if (response.statusCode == 200) {
      final List<Object?> jsonData = jsonDecode(response.body) as List<Object?>;
      return SearchResults.fromJson(jsonData);
    } else {
      throw HttpException(
        '[WikimediaApiClient.getArticleByTitle] '
        'statusCode=${response.statusCode}, '
        'body=${response.body}',
      );
    }
  } on FormatException {
    rethrow;
  } finally {
    client.close();
  }
}

```
> This code defines the `search` function, which uses the `http` package to make a GET request to the Wikipedia API's `opensearch` endpoint and returns a `SearchResults` object. The `opensearch` endpoint is used to search for Wikipedia articles based on a search term.

> 6. Create the file `wikipedia/lib/src/api/get_article.dart`.
> 7. Add the following code to `wikipedia/lib/src/api/get_article.dart`:

```dart
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../model/article.dart';

Future<List<Article>> getArticleByTitle(String title) async {
  final http.Client client = http.Client();
  try {
    final Uri url = Uri.https(
      'en.wikipedia.org',
      '/w/api.php',
      <String, Object?>{
        // order matters - explaintext must come after prop
        'action': 'query',
        'format': 'json',
        'titles': title.trim(),
        'prop': 'extracts',
        'explaintext': '',
      },
    );
    final http.Response response = await client.get(url);
    if (response.statusCode == 200) {
      final Map<String, Object?> jsonData =
          jsonDecode(response.body) as Map<String, Object?>;
      return Article.listFromJson(jsonData);
    } else {
      throw HttpException(
        '[ApiClient.getArticleByTitle] '
        'statusCode=${response.statusCode}, '
        'body=${response.body}',
      );
    }
  } on FormatException {
    // TODO: log
    rethrow;
  } finally {
    client.close();
  }
}

```

:::tip
```dart
final jsonData = jsonDecode(response.body).cast<Map<String, Object?>>();
```
使用`cast<>()`而非`as`会*更安全* ，如果类型不对不会Panic
:::

> This code defines the `getArticleByTitle` function, which uses the `http` package to make a GET request to the Wikipedia API and returns a `List<Article>` object. This function retrieves the content of a Wikipedia article based on its title.

### 导出API函数 Export the API functions
> Now that you've created the API functions, you need to export them from the `wikipedia` library so that they can be used by the `cli` package. You'll also export the existing models.
> 1. Open the `wikipedia/lib/wikipedia.dart` file.
> 2. Add the following `export` statements to the file:

```dart
export 'src/api/get_article.dart';
export 'src/api/search.dart';
export 'src/api/summary.dart';
export 'src/model/article.dart';
export 'src/model/search_results.dart';
export 'src/model/summary.dart';
export 'src/model/title_set.dart';

```
> These `export` statements make the API functions and models available to other packages that depend on the `wikipedia` package.

### 运行先前的测试样例 Verify with tests
> Now that you have implemented the API functions and updated the package dependencies, it's good practice to run the tests you created in the previous chapter. This will confirm that your changes have not broken the existing functionality of the `wikipedia` package.
> 1. Open your terminal and navigate to the `wikipedia/test` directory.
> 2. Remove the default test file by running the command `rm wikipedia_test.dart` (on macOS or Linux) or `del wikipedia_test.dart` (on Windows). This file was generated automatically but is not used in our project.
> 3. Open your terminal and navigate to the `wikipedia` directory.
> 4. Run the command `dart test`.
> 	You should see output similar to this, confirming all your existing tests still pass:
```bash
00:02 +3: All tests passed!
This confirms that the wikipedia package is still working as expected.

```

![](assets/Pasted%20image%2020260503205319.png)
*pub get的问题仍然没有解决，先凑合着用*

### 课后练习
#### 如何使用`Uri.https`构造带查询参数的URL
> **How do you construct a URL with query parameters using `Uri.https`?**
```MArkdown
Pass them as a third argument map: `Uri.https('api.com', '/search', {'q': 'dart'})`
```
> The third parameter accepts a `Map<String, dynamic>` of query parameters. Dart handles URL encoding automatically.

#### 你该怎么知道请求是否成功呢
> **After calling `client.get(url)`, how should you check if the request was successful?**
```Markdown
Check if `response.statusCode == 200` (or another success code).
```
> HTTP status codes indicate success (200-299) or various failures (400s, 500s). Always check before processing the response body.

#### 为什么要在`finally`库里调用`client.close()`
> **The lesson's API functions use a `finally` block to call `client.close()`. Why is this important?**
```Markdown
To ensure network resources are released even if an exception occurs.
```
> `finally` runs whether the try block succeeds or throws. This ensures the client's connections are properly closed, preventing resource leaks.

## 增加调试和监控日志 Add logging for debugging and monitoring
> In this chapter, you'll add logging to the `dartpedia` CLI application to help track errors and monitor its behavior. This will involve adding the `logging` package, creating a `Logger` instance, and writing log messages to a file.

### 补充依赖 Add the `logging` dependency
> First, add the `logging` package to your project's dependencies.
> 1. Open the `cli/pubspec.yaml` file.
> 2. Locate the `dependencies` section.
> 3. Add the `logging` package to your dependencies:

```yaml
dependencies:
  http: ^1.3.0
  command_runner:
    path: ../command_runner
  wikipedia:
    path: ../wikipedia
  # Add the following line
  logging: ^1.2.0

```

> 4. Run `dart pub get` in the `cli` directory to fetch the new dependency.

### 创建并配置日志记录器 Create logger
> Next, create a `Logger` instance and configure it to write log messages to a file. This involves creating a new file for the logger and setting up the necessary imports.
> 1. Create a new file called `cli/lib/src/logger.dart`.
> 2. Add the necessary imports and define the `initFileLogger` function.

```dart
import 'dart:io';
import 'package:logging/logging.dart';

Logger initFileLogger(String name) {
  // Enables logging from child loggers.
  hierarchicalLoggingEnabled = true;

  // Create a logger instance with the provided name.
  final logger = Logger(name);
  final now = DateTime.now();

  // The rest of the function will be added below.
  // ...

  return logger;
}

```

> 3. Add the code to find the project's root directory, create a `logs` directory if one doesn't exist, and create a unique log file.
```dart
Logger initFileLogger(String name) {
  hierarchicalLoggingEnabled = true;
  final logger = Logger(name);
  final now = DateTime.now();

  // Get the path to the project directory from the current script.
  final scriptFile = File(Platform.script.toFilePath());
  final projectDir = scriptFile.parent.parent.path;

  // Create a 'logs' directory if it doesn't exist.
  final dir = Directory('$projectDir/logs');
  if (!dir.existsSync()) dir.createSync();

  // Create a log file with a unique name based on
  // the current date and logger name.
  final logFile = File(
    '${dir.path}/${now.year}_${now.month}_${now.day}_$name.txt',
  );

  // The rest of the function will be added below.
  // ...

  return logger;
}

```

> 4. Configure the logger's level and set up a listener to write log messages to the file.
```dart
Logger initFileLogger(String name) {
  hierarchicalLoggingEnabled = true;
  final logger = Logger(name);
  final now = DateTime.now();

  final scriptFile = File(Platform.script.toFilePath());
  final projectDir = scriptFile.parent.parent.path;
  final dir = Directory('$projectDir/logs');
  if (!dir.existsSync()) dir.createSync();
  final logFile = File(
    '${dir.path}/${now.year}_${now.month}_${now.day}_$name.txt',
  );

  // Set the logger level to ALL, so it logs all messages regardless of severity.
  // Level.ALL is useful for development and debugging, but you'll likely want to
  // use a more restrictive level like Level.INFO or Level.WARNING in production.
  logger.level = Level.ALL;

  // Listen for log records and write each one to the log file.
  logger.onRecord.listen((record) {
    final msg =
        '[${record.time} - ${record.loggerName}] ${record.level.name}: ${record.message}';
    logFile.writeAsStringSync('$msg \n', mode: FileMode.append);
  });

  return logger;
}

```
> This code does the following:
- It enables hierarchical logging using `hierarchicalLoggingEnabled = true`.
- It creates a `Logger` instance with the given name.
- It gets the project directory from the `Platform.script.path`.
- It creates a `logs` directory if it doesn't exist.
- It creates a log file with the current date and the logger name.
- It sets the logger level to `Level.ALL`, meaning it will log all messages. This is useful for development and debugging, but you'll likely want to use a more restrictive level like `Level.INFO` or `Level.WARNING` in production.
- It listens for log records and writes them to the log file.

> 5. Create a new file called `cli/lib/cli.dart` and export `logger.dart`. This makes the `initFileLogger` available to other parts of your app.

```dart
 export 'src/commands/get_article.dart';
 export 'src/commands/search.dart';
 export 'src/logger.dart';

```

### 在`cli.dart`中使用`logger` Use the logger in `cli.dart`
> Now, use the `initFileLogger` function in `cli/bin/cli.dart` to create a logger instance and log messages to a file.
> 1. Open the `cli/bin/cli.dart` file.
> 2. Add the import for the logger:

```dart
import 'package:cli/cli.dart';
import 'package:command_runner/command_runner.dart';

```

> 3. Modify the `main` function to initialize the logger and pass it to the commands:

```dart
import 'package:cli/cli.dart';
import 'package:command_runner/command_runner.dart';

void main(List<String> arguments) async {
  final errorLogger = initFileLogger('errors');
  final app =
      CommandRunner(
          onOutput: (String output) async {
            await write(output);
          },
          onError: (Object error) {
            if (error is Error) {
              errorLogger.severe(
                '[Error] ${error.toString()}\n${error.stackTrace}',
              );
              throw error;
            }
            if (error is Exception) {
              errorLogger.warning(error);
            }
          },
        )
        ..addCommand(HelpCommand())
        ..addCommand(SearchCommand(logger: errorLogger))
        ..addCommand(GetArticleCommand(logger: errorLogger));

  app.run(arguments);
}

```

> This code does the following:
- It initializes a `Logger` instance using `initFileLogger('errors')`.
- It passes the `logger` instance to `CommandRunner` and individual commands.

### 编写 `SearchCommand` 指令 Create the SearchCommand command
> The core functionality of the CLI lives in its commands. Create the `SearchCommand` and `GetArticleCommand` files and add the necessary code, including the logging and error handling.
> 1. Create a new file named `/cli/lib/src/commands/search.dart`.
> 2. Add the imports and a basic class structure. This `SearchCommand` class extends `Command`, and its constructor accepts a `Logger` instance. Accepting the logger in the constructor is a common pattern called dependency injection, which allows the command to log events without needing to create its own logger.

```dart
import 'dart:async';
import 'dart:io';

import 'package:command_runner/command_runner.dart';
import 'package:logging/logging.dart';
import 'package:wikipedia/wikipedia.dart';

class SearchCommand extends Command {
  SearchCommand({required this.logger});

  final Logger logger;

  @override
  String get description => 'Search for Wikipedia articles.';

  @override
  bool get requiresArgument => true;

  @override
  String get name => 'search';

  @override
  String get valueHelp => 'STRING';

  @override
  String get help =>
      'Prints a list of links to Wikipedia articles that match the given term.';

  @override
  FutureOr<String> run(ArgResults args) async {
    // The rest of the function will be added below.
    // ...
  }
}

```

> 3. Now, add the core logic to the `run` method. This code checks for a valid argument, calls the `search()` function from the `wikipedia` package, formats the results, and returns the results as a string.

```dart
import 'dart:async';
import 'dart:io';

import 'package:command_runner/command_runner.dart';
import 'package:logging/logging.dart';
import 'package:wikipedia/wikipedia.dart';

class SearchCommand extends Command {
  SearchCommand({required this.logger});

  final Logger logger;

  @override
  String get description => 'Search for Wikipedia articles.';

  @override
  bool get requiresArgument => true;

  @override
  String get name => 'search';

  @override
  String get valueHelp => 'STRING';

  @override
  String get help =>
      'Prints a list of links to Wikipedia articles that match the given term.';

  @override
  FutureOr<String> run(ArgResults args) async {
    if (requiresArgument &&
        (args.commandArg == null || args.commandArg!.isEmpty)) {
      return 'Please include a search term';
    }

    final buffer = StringBuffer('Search results:');
    final SearchResults results = await search(args.commandArg!);

    for (var result in results.results) {
      buffer.writeln('${result.title} - ${result.url}');
    }
    return buffer.toString();
  }
}

```

> 4. Next, add the "I'm feeling lucky" feature by adding a flag to the constructor. Then, in the `run` method, add the logic to check if the flag is set and, if so, get the summary of the top search result.

```dart
import 'dart:async';
import 'dart:io';

import 'package:command_runner/command_runner.dart';
import 'package:logging/logging.dart';
import 'package:wikipedia/wikipedia.dart';

class SearchCommand extends Command {
  SearchCommand({required this.logger}) {
    addFlag(
      'im-feeling-lucky',
      help:
          'If true, prints the summary of the top article that the search returns.',
    );
  }

  final Logger logger;

  @override
  String get description => 'Search for Wikipedia articles.';

  @override
  bool get requiresArgument => true;

  @override
  String get name => 'search';

  @override
  String get valueHelp => 'STRING';

  @override
  String get help =>
      'Prints a list of links to Wikipedia articles that match the given term.';

  @override
  FutureOr<String> run(ArgResults args) async {
    if (requiresArgument &&
        (args.commandArg == null || args.commandArg!.isEmpty)) {
      return 'Please include a search term';
    }

    final buffer = StringBuffer('Search results:');
    final SearchResults results = await search(args.commandArg!);

    if (args.flag('im-feeling-lucky')) {
      final title = results.results.first.title;
      final Summary article = await getArticleSummaryByTitle(title);
      buffer.writeln('Lucky you!');
      buffer.writeln(article.titles.normalized.titleText);
      if (article.description != null) {
        buffer.writeln(article.description);
      }
      buffer.writeln(article.extract);
      buffer.writeln();
      buffer.writeln('All results:');
    }

    for (var result in results.results) {
      buffer.writeln('${result.title} - ${result.url}');
    }
    return buffer.toString();
  }
}

```

> 5. Finally, wrap the main logic in a `try/catch` block. This allows you to handle potential exceptions that could arise from network issues or data formatting problems. You'll use the injected `logger` to record these errors to the log file.

```dart
import 'dart:async';
import 'dart:io';

import 'package:command_runner/command_runner.dart';
import 'package:logging/logging.dart';
import 'package:wikipedia/wikipedia.dart';

class SearchCommand extends Command {
  SearchCommand({required this.logger}) {
    addFlag(
      'im-feeling-lucky',
      help:
          'If true, prints the summary of the top article that the search returns.',
    );
  }

  final Logger logger;

  @override
  String get description => 'Search for Wikipedia articles.';

  @override
  bool get requiresArgument => true;

  @override
  String get name => 'search';

  @override
  String get valueHelp => 'STRING';

  @override
  String get help =>
      'Prints a list of links to Wikipedia articles that match the given term.';

  @override
  FutureOr<String> run(ArgResults args) async {
    if (requiresArgument &&
        (args.commandArg == null || args.commandArg!.isEmpty)) {
      return 'Please include a search term';
    }

    final buffer = StringBuffer('Search results:');
    try {
      final SearchResults results = await search(args.commandArg!);

      if (args.flag('im-feeling-lucky')) {
        final title = results.results.first.title;
        final Summary article = await getArticleSummaryByTitle(title);
        buffer.writeln('Lucky you!');
        buffer.writeln(article.titles.normalized.titleText);
        if (article.description != null) {
          buffer.writeln(article.description);
        }
        buffer.writeln(article.extract);
        buffer.writeln();
        buffer.writeln('All results:');
      }

      for (var result in results.results) {
        buffer.writeln('${result.title} - ${result.url}');
      }
      return buffer.toString();
    } on HttpException catch (e) {
      logger
        ..warning(e.message)
        ..warning(e.uri)
        ..info(usage);
      return e.message;
    } on FormatException catch (e) {
      logger
        ..warning(e.message)
        ..warning(e.source)
        ..info(usage);
      return e.message;
    }
  }
}

```

### 编写 `GetArticleCommand` 指令 Create the GetArticleCommand command
> Now, create the `GetArticleCommand` file and add the necessary code. The code is similar to the previous `SearchCommand`, as it also uses a `try/catch` block to handle potential network or data errors.
> 1. Create a new file named cli/lib/src/commands/get_article.dart.
> 2. Add the following code to `get_article.dart`.

```dart
import 'dart:async';
import 'dart:io';

import 'package:command_runner/command_runner.dart';
import 'package:logging/logging.dart';
import 'package:wikipedia/wikipedia.dart';

class GetArticleCommand extends Command {
  GetArticleCommand({required this.logger});

  final Logger logger;

  @override
  String get description => 'Read an article from Wikipedia';

  @override
  String get name => 'article';

  @override
  String get help => 'Gets an article by exact canonical wikipedia title.';

  @override
  String get defaultValue => 'cat';

  @override
  String get valueHelp => 'STRING';

  @override
  FutureOr<String> run(ArgResults args) async {
    try {
      var title = args.commandArg ?? defaultValue;
      final List<Article> articles = await getArticleByTitle(title);
      // API returns a list of articles, but we only care about the closest hit.
      final article = articles.first;
      final buffer = StringBuffer('\n=== ${article.title.titleText} ===\n\n');
      buffer.write(article.extract.split(' ').take(500).join(' '));
      return buffer.toString();
    } on HttpException catch (e) {
      logger
        ..warning(e.message)
        ..warning(e.uri)
        ..info(usage);
      return e.message;
    } on FormatException catch (e) {
      logger
        ..warning(e.message)
        ..warning(e.source)
        ..info(usage);
      return e.message;
    }
  }
}

```
> Review the code you've just added. The `SearchCommand` and `GetArticleCommand` now:

- Import the necessary packages like `command_runner`, `logging`, and `wikipedia` to use their classes and functions.
- Accept a `Logger` instance through their constructor. This is a common pattern called dependency injection, which allows the command to log events without needing to create its own logger.
- Implement a `run` method that defines the command's logic. This method calls the appropriate wikipedia API and formats the output.
- Include `try/catch` blocks to gracefully handle network errors (`HttpException`) and data parsing errors (`FormatException`), logging them for debugging.

### 运行程序并检查日志 Run the application and check the logs
> Now that you've added logging to your application, run it and check the log file to see the results.
> 1. Run the application with a command that might produce an error. For example, try searching for an article that doesn't exist or that causes a `FormatException`.
```bash
dart run bin/cli.dart search blahblahblahblah

```

![](assets/Pasted%20image%2020260503221436.png)
呵呵

### 课后练习
#### `logging`库的作用是什么
> **What is the purpose of the `logging` package in Dart?**
```Markdown
To provide a way to record events and errors in your application.
```
> The `logging` package provides a flexible system for recording events, warnings, errors, and other messages during application execution.

#### `hierarchicalLoggingEnabled = true;`这行的作用是什么
> **What does the `hierarchicalLoggingEnabled = true;` line do?**\
```Markdown
It enables a logger to capture events from child loggers.
```
> With hierarchical logging enabled, parent loggers can receive and process events from their child loggers.

#### 为什么日志记录器有这么多不同的日志级别？为什么不直接使用`print()`？
> **This lesson uses `logger.severe()`, `logger.warning()`, and `logger.info()`. Why use different log levels instead of just `print()`?**
```Markdown
You can filter logs by severity, showing only warnings and errors in production while seeing everything during development.
```
> Log levels let you set a threshold. In production, you might only log warnings and above, while in development you see info and debug messages too.


***
# 页面底部