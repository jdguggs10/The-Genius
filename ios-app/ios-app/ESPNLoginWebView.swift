import SwiftUI
import WebKit // Required for HTTPCookie

private let appBackgroundColor = Color(red: 253/255, green: 245/255, blue: 230/255) // FDF5E6
private let appPrimaryFontColor = Color(red: 61/255, green: 108/255, blue: 104/255) // 3D6C68

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
                        .foregroundColor(appPrimaryFontColor) // Apply theme color
                    }
                }
            } else {
                VStack {
                    Spacer()
                    Image(systemName: "exclamationmark.triangle.fill") // SF Symbol for error
                        .font(.largeTitle)
                        .foregroundColor(.orange) // Keep orange for warning/error
                        .padding(.bottom)
                    Text("Error: Invalid Login URL")
                        .foregroundColor(appPrimaryFontColor.opacity(0.8))
                    Spacer()
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(appBackgroundColor.edgesIgnoringSafeArea(.all))
                .navigationTitle("Error")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .navigationBarLeading) {
                        Button("Done") { // "Done" makes sense if an error page is shown
                            dismiss()
                        }
                        .foregroundColor(appPrimaryFontColor) // Apply theme color
                    }
                }
            }
        }
        // It's often better to set the background on the content inside NavigationStack if conditional
        // or on the NavigationStack itself if it should always apply.
        // For this case, error view gets its own background.
        // The WebView will dominate if URL is valid.
    }
}

#Preview {
    ESPNLoginWebView()
}
