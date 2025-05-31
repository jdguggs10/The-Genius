import Foundation

class ESPNCookieManager {
    static let shared = ESPNCookieManager()

    private let espnS2Key = "espn_s2_cookie"
    private let swidKey = "swid_cookie"

    private init() {} // Private initializer to ensure singleton usage

    func saveCookies(espnS2: String, swid: String) {
        UserDefaults.standard.set(espnS2, forKey: espnS2Key)
        UserDefaults.standard.set(swid, forKey: swidKey)
        print("ESPNCookieManager: Saved espn_s2 and SWID cookies to UserDefaults.")
    }

    func getCookies() -> (espnS2: String?, swid: String?) {
        let espnS2 = UserDefaults.standard.string(forKey: espnS2Key)
        let swid = UserDefaults.standard.string(forKey: swidKey)
        // For debugging:
        // print("ESPNCookieManager: Retrieved espn_s2: \(espnS2 ?? "nil"), SWID: \(swid ?? "nil") from UserDefaults.")
        return (espnS2, swid)
    }

    func getCookieHeader() -> String? {
        let cookies = getCookies()
        if let espnS2 = cookies.espnS2, let swid = cookies.swid {
            return "SWID=\(swid); espn_s2=\(espnS2)"
        }
        return nil
    }

    func clearCookies() {
        UserDefaults.standard.removeObject(forKey: espnS2Key)
        UserDefaults.standard.removeObject(forKey: swidKey)
        print("ESPNCookieManager: Cleared espn_s2 and SWID cookies from UserDefaults.")
    }
}
