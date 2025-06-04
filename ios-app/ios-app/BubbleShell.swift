//
//  BubbleShell.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//

import SwiftUI

struct BubbleShell<Content: View>: View {
    let corners: UIRectCorner
    let content: () -> Content
    
    var body: some View {
        content()
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .clipShape(RoundedCorner(radius: 16, corners: corners))
    }
}

// Custom RoundedCorner shape for message bubbles
struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners

    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(roundedRect: rect, byRoundingCorners: corners, cornerRadii: CGSize(width: radius, height: radius))
        return Path(path.cgPath)
    }
}

#Preview {
    VStack {
        BubbleShell(corners: [.topLeft, .bottomLeft, .topRight]) {
            Text("User bubble")
                .foregroundColor(.white)
        }
        .background(Color.blue)
        
        BubbleShell(corners: [.topRight, .bottomRight, .topLeft]) {
            Text("Assistant bubble")
                .foregroundColor(.black)
        }
        .background(Color.gray.opacity(0.2))
    }
    .padding()
} 