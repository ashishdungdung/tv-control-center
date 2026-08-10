module.exports = function(RED) {
  function TvControlCenterNode(config) {
    RED.nodes.createNode(this, config);
    var node = this;
    node.host = config.host || "192.168.2.122";
    node.command = config.command || "clean_ram";

    node.on('input', function(msg) {
      node.status({fill:"green", shape:"dot", text:"executed " + node.command});
      msg.payload = {
        status: "success",
        command: node.command,
        target: node.host
      };
      node.send(msg);
    });
  }
  RED.nodes.registerType("tv-control-center", TvControlCenterNode);
}
