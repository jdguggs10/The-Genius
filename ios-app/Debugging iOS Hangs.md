## **Executive Summary**

  

Hangs in iOS apps almost always trace back to work that blocks the **main thread**—either because that thread is _busy_ crunching on heavy tasks or _blocked_ waiting for a resource that will never come. The most frequent villains are synchronous Grand-Central-Dispatch (GCD) calls, deadlocks between queues, runaway SwiftUI updates, memory-pressure stalls, and slow rendering caused by Auto Layout or image decoding. Modern Apple tooling (Instruments Hang template, Main-Thread Checker, Xcode Organizer hang metrics) paired with third-party watchers (Sentry, Firebase) lets you capture, classify, and fix these issues quickly. Read on for a detailed field manual your AI coding agents can automate.

---

## **1 ▸ What Exactly Is a Hang?**

|**Type**|**Symptom**|**Diagnostic Clue**|
|---|---|---|
|**Busy Main Thread**|CPU pegs, UI ignores taps|Thread 0 shows continuous stack change in Instruments Hang trace ([developer.apple.com](https://developer.apple.com/tutorials/instruments/identifying-a-hang?utm_source=chatgpt.com))|
|**Blocked Main Thread**|CPU idle, UI frozen|Thread 0 parked on semaphore_wait_trap or mach_msg_trap ([developer.apple.com](https://developer.apple.com/tutorials/instruments/getting-started-with-hang-analysis?utm_source=chatgpt.com))|
|**Watchdog Termination**|App killed after ~16 s unresponsiveness|Crash log with 0x8badf00d|

> **Thresholds**: Apple's Performance team recommends keeping any single main-thread job under **100 ms** and avoiding cumulative busy time > 250 ms per interaction. ([developer.apple.com](https://developer.apple.com/videos/play/wwdc2023/10248/?utm_source=chatgpt.com))

---

## **2 ▸ Toolbox for Tracking Stalls**

  

### **2.1 Apple First-Party**

- **Instruments ▸ Hang Analysis** – differentiates busy vs blocked main thread and pinpoints culprit stacks. ([developer.apple.com](https://developer.apple.com/tutorials/instruments/identifying-a-hang?utm_source=chatgpt.com))
    
- **Main-Thread Checker** – real-time alerts for UI APIs mis-called off main actor. ([developer.apple.com](https://developer.apple.com/documentation/xcode/analyzing-the-performance-of-your-shipping-app?utm_source=chatgpt.com))
    
- **Xcode Organizer ▸ Hang Rate** – aggregates TestFlight/App Store spin-traces to show field impact. ([developer.apple.com](https://developer.apple.com/documentation/xcode/analyzing-the-performance-of-your-shipping-app?utm_source=chatgpt.com))
    
- **On-device Hang Detection (iOS 15+)** – captures spin-traces even outside debug builds. ([developer.apple.com](https://developer.apple.com/videos/play/wwdc2022/10082/?utm_source=chatgpt.com))
    

  

### **2.2 Third-Party Watchers**

- **Sentry AppHangTracker** – watchdog thread posts a task to main queue every 2 s and reports when not serviced. ([docs.sentry.io](https://docs.sentry.io/platforms/apple/guides/ios/configuration/app-hangs/?utm_source=chatgpt.com))
    
- **Firebase Performance ▸ Frozen Frame traces** – flags frames > 700 ms and allows alerting when frozen frames exceed 1 %. ([firebase.google.com](https://firebase.google.com/docs/perf-mon/screen-traces?utm_source=chatgpt.com), [firebase.google.com](https://firebase.google.com/docs/perf-mon/alerts?utm_source=chatgpt.com))
    

---

## **3 ▸ Root Causes & Tactical Fixes**

  

### **3.1 Main-Thread Congestion (the "80 % Problem")**

- **Synchronous APIs**: dispatch_sync, performAndWait, URLSession.sendSynchronousRequest – all block until done. Calling these on the main queue or re-entering the same serial queue deadlocks. ([stackoverflow.com](https://stackoverflow.com/questions/18297118/deadlock-with-dispatch-sync?utm_source=chatgpt.com), [donnywals.com](https://www.donnywals.com/understanding-how-dispatchqueue-sync-can-cause-deadlocks/?utm_source=chatgpt.com))
    
- **Heavy CPU in UI Callbacks**: JSON parsing, Core Graphics drawing, zipping files. Move to a background Task { }, then hop back to @MainActor for UI.
    
- **Expensive Image Decoding/Filtering**: Use down-scaled thumbnails and decode off-thread; leverage CGImageSourceCreateThumbnailAtIndex.
    

  

### **3.2 Deadlocks & Serial-Queue Misfires**

- Classic pattern: you're _already_ on queue Q, then dispatch_sync to Q again – app locks indefinitely. ([stackoverflow.com](https://stackoverflow.com/questions/18297118/deadlock-with-dispatch-sync?utm_source=chatgpt.com))
    
- Guard by checking Thread.isMainThread before any synchronous dispatch; prefer async or Swift concurrency.
    

  

### **3.3 Infinite Loops & Runaway Recursion**

- **SwiftUI State Bombs**: Changing state inside .onAppear that triggers the same view hierarchy again forms an infinite render loop. ([stackoverflow.com](https://stackoverflow.com/questions/77865159/swiftui-navigation-link-infinite-loop-causes-app-to-freeze?utm_source=chatgpt.com), [developer.apple.com](https://developer.apple.com/forums/thread/750514?utm_source=chatgpt.com))
    
- **Notification Storms / Timers**: Verify observers de-register and timers invalidate.
    
- **Debug**: Pause debugger – if back-trace repeats the same function hundreds of frames, you've hit a loop.
    

  

### **3.4 Layout & Rendering Bottlenecks**

- Constraint explosions in UICollectionView with self-sizing cells can cost dozens of ms per cell. Profile with Instruments ▸ Core Animation. ([developer.apple.com](https://developer.apple.com/videos/play/wwdc2023/10248/?utm_source=chatgpt.com))
    
- Cache calculated heights; pre-render text with UILabel.preferredMaxLayoutWidth.
    

  

### **3.5 Memory Pressure & Retain Cycles**

- Retained UIViewController graphs via strong closures balloon RAM; once iOS starts paging, every view interaction stalls. ([medium.com](https://medium.com/%40koteshpatel6/understanding-ios-memory-leaks-causes-examples-and-how-to-avoid-them-23c22dcbc4a0?utm_source=chatgpt.com), [stackoverflow.com](https://stackoverflow.com/questions/32534316/ios-memory-management-leaks-retain-cycles?utm_source=chatgpt.com))
    
- Run **Instruments ▸ Leaks** and **Allocations**; watch "Persistent bytes". Break cycles with [weak self] or unowned where safe.
    

  

### **3.6 Persistence Threads (Core Data)**

- Accessing NSManagedObject from the wrong queue or using performAndWait on main thread during scrolling blocks UI. ([stackoverflow.com](https://stackoverflow.com/questions/16376543/nsmanagedobjectcontext-performblockandwait-causing-deadlock-when-called-from-two?utm_source=chatgpt.com), [developer.apple.com](https://developer.apple.com/documentation/coredata/using_core_data_in_the_background?changes=_4&utm_source=chatgpt.com))
    
- Strategy: create a background NSPersistentContainer.newBackgroundContext(), perform work there, pass object IDs back to UI.
    

  

### **3.7 Networking & I/O Mismanagement**

- Blocking file reads (Data(contentsOf:)) or large sync URLSession loads lock UI. Stream to disk and decode off-thread.
    
- Use URLSession async/await plus URLSessionConfiguration.waitsForConnectivity to avoid stalling connection attempts.
    

  

### **3.8 Third-Party SDK Misbehavior**

- Analytics or Ad SDKs sometimes dispatch blocking work on main. Use Time Profiler to attribute stack to framework; lazy-load heavy SDKs post-launch.
    

---

## **4 ▸ Diagnostic Playbook Your AI Agent Can Automate**

1. **Attach Instruments Hang Analysis** to physical device; reproduce freeze.
    
2. Classify trace as Busy vs Blocked; if busy, open **CPU Profiler** and capture heavy stack; if blocked, inspect waiting thread's queues/semaphores.
    
3. Run **Main-Thread Checker** in debug runs; fail build if violations appear.
    
4. Schedule nightly uploads of Organizer Hang metrics; regress if hang rate > 0.1 per 100 launches.
    
5. Add **os_signpost** markers around all async hops; chart signpost intervals to detect > 100 ms spans. ([developer.apple.com](https://developer.apple.com/videos/play/wwdc2023/10248/?utm_source=chatgpt.com))
    
6. Enable Sentry enableAppHangTracking = true and Firebase frozen-frames alerts at 1 %. ([docs.sentry.io](https://docs.sentry.io/platforms/apple/guides/ios/configuration/app-hangs/?utm_source=chatgpt.com), [firebase.google.com](https://firebase.google.com/docs/perf-mon/alerts?utm_source=chatgpt.com))
    

---

## **5 ▸ Proactive Prevention**

- **Design for Concurrency** – adopt Swift Concurrency (async/await, actors) from the outset; treat any UI callback as strictly presentational.
    
- **Unit Tests for Long-Running Tasks** – measure functions with XCTMeasure to ensure < 50 ms budget.
    
- **CI Gate** – run a headless UI test with Instruments Hang template; fail pull request if any busy segment > 250 ms.
    
- **Memory Regression Budgets** – fail builds if resident memory grows > 20 MB after a standard navigation script.
    

---

## **References**

1. Identifying a hang — Apple Instruments Tutorial ([developer.apple.com](https://developer.apple.com/tutorials/instruments/identifying-a-hang?utm_source=chatgpt.com))
    
2. Analyze hangs with Instruments — WWDC23 Session 10248 ([developer.apple.com](https://developer.apple.com/videos/play/wwdc2023/10248/?utm_source=chatgpt.com))
    
3. Busy vs Blocked main thread — Apple Instruments Tutorial ([developer.apple.com](https://developer.apple.com/tutorials/instruments/getting-started-with-hang-analysis?utm_source=chatgpt.com))
    
4. Deadlock with dispatch_sync — StackOverflow ([stackoverflow.com](https://stackoverflow.com/questions/18297118/deadlock-with-dispatch-sync?utm_source=chatgpt.com))
    
5. Understanding Dispatch Sync deadlocks — Donny Wals Blog ([donnywals.com](https://www.donnywals.com/understanding-how-dispatchqueue-sync-can-cause-deadlocks/?utm_source=chatgpt.com))
    
6. SwiftUI Navigation infinite loop freeze — StackOverflow ([stackoverflow.com](https://stackoverflow.com/questions/77865159/swiftui-navigation-link-infinite-loop-causes-app-to-freeze?utm_source=chatgpt.com))
    
7. Infinite loop refreshing view — Apple Dev Forums ([developer.apple.com](https://developer.apple.com/forums/thread/750514?utm_source=chatgpt.com))
    
8. performBlockAndWait deadlock — StackOverflow ([stackoverflow.com](https://stackoverflow.com/questions/16376543/nsmanagedobjectcontext-performblockandwait-causing-deadlock-when-called-from-two?utm_source=chatgpt.com))
    
9. Core Data in background — Apple Docs ([developer.apple.com](https://developer.apple.com/documentation/coredata/using_core_data_in_the_background?changes=_4&utm_source=chatgpt.com))
    
10. Memory leaks & retain cycles — Medium ([medium.com](https://medium.com/%40koteshpatel6/understanding-ios-memory-leaks-causes-examples-and-how-to-avoid-them-23c22dcbc4a0?utm_source=chatgpt.com))
    
11. iOS memory leaks overview — StackOverflow ([stackoverflow.com](https://stackoverflow.com/questions/32534316/ios-memory-management-leaks-retain-cycles?utm_source=chatgpt.com))
    
12. Analyzer hang metrics — Xcode Organizer Guide ([developer.apple.com](https://developer.apple.com/documentation/xcode/analyzing-the-performance-of-your-shipping-app?utm_source=chatgpt.com))
    
13. Track hangs with on-device detection — WWDC22 Session 10082 ([developer.apple.com](https://developer.apple.com/videos/play/wwdc2022/10082/?utm_source=chatgpt.com))
    
14. Sentry App Hang Tracker docs ([docs.sentry.io](https://docs.sentry.io/platforms/apple/guides/ios/configuration/app-hangs/?utm_source=chatgpt.com))
    
15. Firebase frozen frames & alerts — Firebase Docs ([firebase.google.com](https://firebase.google.com/docs/perf-mon/screen-traces?utm_source=chatgpt.com), [firebase.google.com](https://firebase.google.com/docs/perf-mon/alerts?utm_source=chatgpt.com))

## **Swift Concurrency Best Practices**

@MainActor
class ViewModel: ObservableObject {
    @Published var data: [Item] = []
    
    func loadData() async {
        // This runs on background
        let items = await DataService.fetchItems()
        
        // UI update automatically on main thread due to @MainActor
        self.data = items
    }
}

class BadViewModel: ObservableObject {
    @Published var data: [Item] = []
    
    func loadData() {
        // This blocks main thread
        DispatchQueue.main.sync {
            let items = DataService.fetchItemsSync() // Blocking call
            self.data = items
        }
    }
}

// Recommended Approach - Using async function
private func parseSSEData(_ data: String) async -> ParsedResponseComplete? {
    // This automatically runs on a background actor/queue
    guard let jsonData = data.data(using: .utf8) else { return nil }
    
    do {
        let parsed = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any]
        // ... parsing logic
        return ParsedResponseComplete(advice: advice, responseId: responseId)
    } catch {
        return nil
    }
}

// In processSSEEvent
} else if eventType == "response_complete" {
    // Parse on background
    if let parsedResult = await parseSSEData(data) {
        // Update UI on main thread
        await MainActor.run {
            HangDetector.shared.measureMainThreadOperation(
                operation: {
                    var updatedMessage = messages[messageIndex]
                    updatedMessage.content = parsedResult.advice.mainAdvice
                    updatedMessage.structuredAdvice = parsedResult.advice
                    messages[messageIndex] = updatedMessage
                    statusMessage = nil
                    isSearching = false
                },
                description: "UI update for response completion"
            )
        }
    }
}