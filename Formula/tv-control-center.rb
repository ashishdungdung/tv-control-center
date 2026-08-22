class TvControlCenter < Formula
  desc "Universal Smart TV Management Suite for Sony BRAVIA, SHIELD, TCL, Hisense, Fire TV, Chromecast, Xiaomi"
  homepage "https://github.com/ashishdungdung/tv-control-center"
  url "https://files.pythonhosted.org/packages/source/t/tv-control-center/tv_control_center-0.0.4.tar.gz"
  sha256 "70221569ed8949b7f07db13e3c19dffb902e1dde69264cbc4b093830a3d04677"
  license "MIT"

  depends_on "python@3.11"
  depends_on "android-platform-tools"

  def install
    virtualenv_install_with_resources
  end

  service do
    run [opt_bin/"tv-control-center", "serve", "--port", "8888"]
    keep_alive true
    log_path var/"log/tv-control-center.log"
    error_log_path var/"log/tv-control-center.error.log"
  end

  test do
    system "#{bin}/tv-control-center", "--help"
  end
end
