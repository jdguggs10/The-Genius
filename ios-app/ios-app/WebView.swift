import SwiftUI
import WebKit

struct WebView: UIViewRepresentable {
    let url: URL
    var onCookiesAvailable: (([HTTPCookie]) -> Void)?

    init(url: URL, onCookiesAvailable: (([HTTPCookie]) -> Void)? = nil) {
        self.url = url
        self.onCookiesAvailable = onCookiesAvailable
    }

    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()
        webView.navigationDelegate = context.coordinator
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {
        // Only load new request if URL changed or it's the initial load.
        // WKWebView handles its own state for subsequent loads if URL is the same.
        if uiView.url != url || uiView.url == nil {
            let request = URLRequest(url: url)
            uiView.load(request)
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self, onCookiesAvailable: onCookiesAvailable)
    }

    class Coordinator: NSObject, WKNavigationDelegate {
        var parent: WebView
        var onCookiesAvailable: (([HTTPCookie]) -> Void)?

        init(_ parent: WebView, onCookiesAvailable: (([HTTPCookie]) -> Void)?) {
            self.parent = parent
            self.onCookiesAvailable = onCookiesAvailable
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            print("WebView navigation finished for URL: \(webView.url?.absoluteString ?? "Unknown URL")")

            // Check if the loaded URL is the main ESPN page, which is the redirect target after login.
            if webView.url?.absoluteString == "https://www.espn.com/" {
                WKWebsiteDataStore.default().httpCookieStore.getAllCookies { cookies in
                    self.onCookiesAvailable?(cookies)
                }
            }
        }
    }
}
