/* Homebridge plugin for TV Control Center — Universal Smart TV Suite */
let Service, Characteristic;

module.exports = (homebridge) => {
  Service = homebridge.hap.Service;
  Characteristic = homebridge.hap.Characteristic;
  homebridge.registerAccessory("homebridge-tv-control-center", "TVControlCenter", TVControlCenterAccessory);
};

class TVControlCenterAccessory {
  constructor(log, config) {
    self = this;
    this.log = log;
    this.name = config.name || "Smart TV";
    this.host = config.host || "192.168.2.122";
    this.port = config.port || 8888;
    this.activeState = Characteristic.Active.ACTIVE;

    this.tvService = new Service.Television(this.name, "tvService");
    this.tvService.setCharacteristic(Characteristic.ConfiguredName, this.name);
    this.tvService.setCharacteristic(Characteristic.SleepDiscoveryMode, Characteristic.SleepDiscoveryMode.ALWAYS_DISCOVERABLE);

    this.tvService.getCharacteristic(Characteristic.Active)
      .onGet(() => this.activeState)
      .onSet((value) => {
        this.activeState = value;
        this.log.info(`Smart TV Power set to ${value === Characteristic.Active.ACTIVE ? 'ON' : 'OFF'}`);
      });

    this.speakerService = new Service.TelevisionSpeaker(this.name + " Volume", "speakerService");
    this.speakerService.setCharacteristic(Characteristic.Active, Characteristic.Active.ACTIVE);
    this.speakerService.setCharacteristic(Characteristic.VolumeControlType, Characteristic.VolumeControlType.ABSOLUTE);
  }

  getServices() {
    return [this.tvService, this.speakerService];
  }
}
