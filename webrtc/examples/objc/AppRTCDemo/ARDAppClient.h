/*
 *  Copyright 2014 The WebRTC Project Authors. All rights reserved.
 *
 *  Use of this source code is governed by a BSD-style license
 *  that can be found in the LICENSE file in the root of the source
 *  tree. An additional intellectual property rights grant can be found
 *  in the file PATENTS.  All contributing project authors may
 *  be found in the AUTHORS file in the root of the source tree.
 */

#import <Foundation/Foundation.h>

#import "RTCVideoTrack.h"

typedef NS_ENUM(NSInteger, ARDAppClientState) {
  // Disconnected from servers.
  kARDAppClientStateDisconnected,
  // Connecting to servers.
  kARDAppClientStateConnecting,
  // Connected to servers.
  kARDAppClientStateConnected,
};

@class ARDAppClient;
// The delegate is informed of pertinent events and will be called on the
// main queue.
@protocol ARDAppClientDelegate <NSObject>

- (void)appClient:(ARDAppClient *)client
    didChangeState:(ARDAppClientState)state;

- (void)appClient:(ARDAppClient *)client
    didChangeConnectionState:(RTCICEConnectionState)state;

- (void)appClient:(ARDAppClient *)client
    didReceiveLocalVideoTrack:(RTCVideoTrack *)localVideoTrack;

- (void)appClient:(ARDAppClient *)client
    didReceiveRemoteVideoTrack:(RTCVideoTrack *)remoteVideoTrack;

- (void)appClient:(ARDAppClient *)client
         didError:(NSError *)error;

@end

// Handles connections to the AppRTC server for a given room. Methods on this
// class should only be called from the main queue.
@interface ARDAppClient : NSObject

@property(nonatomic, readonly) ARDAppClientState state;
@property(nonatomic, weak) id<ARDAppClientDelegate> delegate;

// Convenience constructor since all expected use cases will need a delegate
// in order to receive remote tracks.
- (instancetype)initWithDelegate:(id<ARDAppClientDelegate>)delegate;

// Establishes a connection with the AppRTC servers for the given room id.
// TODO(tkchin): provide available keys/values for options. This will be used
// for call configurations such as overriding server choice, specifying codecs
// and so on.
- (void)connectToRoomWithId:(NSString *)roomId
                    options:(NSDictionary *)options;

// Disconnects from the AppRTC servers and any connected clients.
- (void)disconnect;

@end