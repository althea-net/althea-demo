const http = require("http");

NODES = {};

function onRequest(req, res) {
  if (req.method == "GET") {
    res.writeHead(200, {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json"
    });
    res.end(JSON.stringify(NODES));
  } else if (req.method == "POST") {
    let jsonString = "";

    req.on("data", function(data) {
      jsonString += data;
    });

    req.on("end", function() {
      const data = JSON.parse(jsonString);
      NODES[data["id"]] = data;
    });
  } else {
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("404 error! File not found.");
  }
}

http.createServer(onRequest).listen(Number(process.argv[2]));
console.log(`Server has started on ${process.argv[2]}`);
