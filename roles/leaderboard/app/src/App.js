import React, { Component } from "react";
import Node from "./Node.js";

// Gotta keep this up to date with <gateway_mesh_ip>:<stat_server_port>
const statServer = "http://192.168.1.233:7779";

function sortNodes(nodes) {
  return Object.keys(nodes)
    .map(key => nodes[key])
    .sort((a, b) => b.total - a.total);
}

class App extends Component {
  constructor(props) {
    super(props);
    this.state = { nodes: [] };
    setInterval(() => {
      this.updateNodes();
    }, 1000);
  }
  async updateNodes() {
    const rand = Math.random();
    console.log("req", rand);
    const rawnodes = await (await fetch(statServer)).json();
    const nodes = sortNodes(rawnodes);
    console.log("res", rand, nodes);
    this.setState({ nodes });
  }
  render() {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          flexWrap: "wrap",
          justifyContent: "center"
        }}
      >
        {this.state.nodes.map((node, i) => (
          <Node
            key={i}
            name={node.id}
            message={node.message}
            total={node.total}
            price={node.price}
            i={i}
          />
        ))}
      </div>
    );
  }
}

export default App;
