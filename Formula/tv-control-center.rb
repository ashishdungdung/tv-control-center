class TvControlCenter < Formula
  desc "Universal Smart TV Management Suite for Sony BRAVIA, SHIELD, TCL, Hisense, Fire TV, Chromecast, Xiaomi"
  homepage "https://github.com/ashishdungdung/tv-control-center"
  url "https://files.pythonhosted.org/packages/source/t/tv-control-center/tv_control_center-0.0.2.tar.gz"
  sha256 "ffdfdab50ed2f1e472faeac7b8dc0056e1d66bb8f02361dbfc1401e9870f6f1c"
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
