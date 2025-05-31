import SwiftUI
import WebKit // Required for HTTPCookie

struct ESPNLoginWebView: View {
    @Environment(\.dismiss) var dismiss
    // @State private var espnS2: String? // Removed, using ESPNCookieManager
    // @State private var swid: String? // Removed, using ESPNCookieManager

    // The new ESPN login URL
    private let loginURLString = "https://secure.web.plus.espn.com/identity/login?redirectUrl=https://www.espn.com/"

    var body: some View {
        NavigationStack {
            if let loginURL = URL(string: loginURLString) {
                WebView(url: loginURL, onCookiesAvailable: { cookies in
                    print("Cookies received in ESPNLoginWebView: \(cookies.count)")
                    var foundEspnS2: String?
                    var foundSwid: String?

                    for cookie in cookies {
                        if cookie.name == "espn_s2" {
                            foundEspnS2 = cookie.value
                            // self.espnS2 = cookie.value // Removed
                            print("Found espn_s2 cookie: \(cookie.value)")
                        } else if cookie.name == "SWID" {
                            foundSwid = cookie.value
                            // self.swid = cookie.value // Removed
                            print("Found SWID cookie: \(cookie.value)")
                        }
                    }

                    // If both cookies are found, save them using ESPNCookieManager and dismiss the view
                    if let s2 = foundEspnS2, let swidValue = foundSwid {
                        ESPNCookieManager.shared.saveCookies(espnS2: s2, swid: swidValue)
                        print("Both espn_s2 and SWID cookies found and saved. Dismissing ESPNLoginWebView.")
                        dismiss()
                    } else {
                        print("Required cookies not found. espn_s2: \(foundEspnS2 ?? "nil"), SWID: \(foundSwid ?? "nil")")
                        // Optionally, handle the case where cookies are not found (e.g., show an error to the user)
                    }
                })
                .navigationTitle("ESPN Login")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .navigationBarLeading) {
                        Button("Cancel") { // Changed "Done" to "Cancel" as "Done" implies completion
                            dismiss()
                        }
                    }
                }
            } else {
                Text("Error: Invalid Login URL")
                    .navigationTitle("Error")
                    .navigationBarTitleDisplayMode(.inline)
                    .toolbar {
                        ToolbarItem(placement: .navigationBarLeading) {
                            Button("Done") {
                                dismiss()
                            }
                        }
                    }
            }
        }
    }
}

#Preview {
    ESPNLoginWebView()
}
