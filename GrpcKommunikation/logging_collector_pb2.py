# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: logging-collector.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import GrpcKommunikation.stream_pb2 as stream__pb2
import GrpcKommunikation.logging_pb2 as logging__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17logging-collector.proto\x12\x18logbee.anne.carl.logging\x1a\x0cstream.proto\x1a\rlogging.proto\"\x92\x03\n\x0fLoggingUpstream\x12>\n\x0cpullLogEvent\x18\x01 \x01(\x0b\x32&.logbee.anne.carl.logging.PullLogEventH\x00\x12-\n\x10\x64ownstreamFinish\x18\x02 \x01(\x0b\x32\x11.DownstreamFinishH\x00\x12/\n\x11\x64ownstreamFailure\x18\x03 \x01(\x0b\x32\x12.DownstreamFailureH\x00\x12/\n\x11upstreamFinishAck\x18\x04 \x01(\x0b\x32\x12.UpstreamFinishAckH\x00\x12\x31\n\x12upstreamFailureAck\x18\x05 \x01(\x0b\x32\x13.UpstreamFailureAckH\x00\x12\x43\n\x08identify\x18\n \x01(\x0b\x32/.logbee.anne.carl.logging.LoggingStreamIdentifyH\x00\x12+\n\x0cinitComplete\x18\x0f \x01(\x0b\x32\x13.StreamInitCompleteH\x00\x42\t\n\x07message\"\x0e\n\x0cPullLogEvent\"\x84\x03\n\x11LoggingDownstream\x12>\n\x0cpushLogEvent\x18\x01 \x01(\x0b\x32&.logbee.anne.carl.logging.PushLogEventH\x00\x12)\n\x0eupstreamFinish\x18\x02 \x01(\x0b\x32\x0f.UpstreamFinishH\x00\x12+\n\x0fupstreamFailure\x18\x03 \x01(\x0b\x32\x10.UpstreamFailureH\x00\x12\x33\n\x13\x64ownstreamFinishAck\x18\x04 \x01(\x0b\x32\x14.DownstreamFinishAckH\x00\x12\x35\n\x14\x64ownstreamFailureAck\x18\x05 \x01(\x0b\x32\x15.DownstreamFailureAckH\x00\x12\x43\n\x08identity\x18\n \x01(\x0b\x32/.logbee.anne.carl.logging.LoggingStreamIdentityH\x00\x12\x1b\n\x04init\x18\x0f \x01(\x0b\x32\x0b.StreamInitH\x00\x42\t\n\x07message\"=\n\x0cPushLogEvent\x12-\n\x08logEvent\x18\x01 \x01(\x0b\x32\x1b.logbee.anne.model.LogEvent\"\x17\n\x15LoggingStreamIdentify\"S\n\x15LoggingStreamIdentity\x12:\n\x08producer\x18\x01 \x01(\x0b\x32(.logbee.anne.model.LogProducerDescriptor2x\n\x10LoggingCollector\x12\x64\n\x04logs\x12+.logbee.anne.carl.logging.LoggingDownstream\x1a).logbee.anne.carl.logging.LoggingUpstream\"\x00(\x01\x30\x01\x42N\n5com.daimler.smartfactory.anne.carl.logging.grpc.protoB\x15LoggingCollectorProtob\x06proto3')



_LOGGINGUPSTREAM = DESCRIPTOR.message_types_by_name['LoggingUpstream']
_PULLLOGEVENT = DESCRIPTOR.message_types_by_name['PullLogEvent']
_LOGGINGDOWNSTREAM = DESCRIPTOR.message_types_by_name['LoggingDownstream']
_PUSHLOGEVENT = DESCRIPTOR.message_types_by_name['PushLogEvent']
_LOGGINGSTREAMIDENTIFY = DESCRIPTOR.message_types_by_name['LoggingStreamIdentify']
_LOGGINGSTREAMIDENTITY = DESCRIPTOR.message_types_by_name['LoggingStreamIdentity']
LoggingUpstream = _reflection.GeneratedProtocolMessageType('LoggingUpstream', (_message.Message,), {
  'DESCRIPTOR' : _LOGGINGUPSTREAM,
  '__module__' : 'logging_collector_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.carl.logging.LoggingUpstream)
  })
_sym_db.RegisterMessage(LoggingUpstream)

PullLogEvent = _reflection.GeneratedProtocolMessageType('PullLogEvent', (_message.Message,), {
  'DESCRIPTOR' : _PULLLOGEVENT,
  '__module__' : 'logging_collector_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.carl.logging.PullLogEvent)
  })
_sym_db.RegisterMessage(PullLogEvent)

LoggingDownstream = _reflection.GeneratedProtocolMessageType('LoggingDownstream', (_message.Message,), {
  'DESCRIPTOR' : _LOGGINGDOWNSTREAM,
  '__module__' : 'logging_collector_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.carl.logging.LoggingDownstream)
  })
_sym_db.RegisterMessage(LoggingDownstream)

PushLogEvent = _reflection.GeneratedProtocolMessageType('PushLogEvent', (_message.Message,), {
  'DESCRIPTOR' : _PUSHLOGEVENT,
  '__module__' : 'logging_collector_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.carl.logging.PushLogEvent)
  })
_sym_db.RegisterMessage(PushLogEvent)

LoggingStreamIdentify = _reflection.GeneratedProtocolMessageType('LoggingStreamIdentify', (_message.Message,), {
  'DESCRIPTOR' : _LOGGINGSTREAMIDENTIFY,
  '__module__' : 'logging_collector_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.carl.logging.LoggingStreamIdentify)
  })
_sym_db.RegisterMessage(LoggingStreamIdentify)

LoggingStreamIdentity = _reflection.GeneratedProtocolMessageType('LoggingStreamIdentity', (_message.Message,), {
  'DESCRIPTOR' : _LOGGINGSTREAMIDENTITY,
  '__module__' : 'logging_collector_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.carl.logging.LoggingStreamIdentity)
  })
_sym_db.RegisterMessage(LoggingStreamIdentity)

_LOGGINGCOLLECTOR = DESCRIPTOR.services_by_name['LoggingCollector']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n5com.daimler.smartfactory.anne.carl.logging.grpc.protoB\025LoggingCollectorProto'
  _LOGGINGUPSTREAM._serialized_start=83
  _LOGGINGUPSTREAM._serialized_end=485
  _PULLLOGEVENT._serialized_start=487
  _PULLLOGEVENT._serialized_end=501
  _LOGGINGDOWNSTREAM._serialized_start=504
  _LOGGINGDOWNSTREAM._serialized_end=892
  _PUSHLOGEVENT._serialized_start=894
  _PUSHLOGEVENT._serialized_end=955
  _LOGGINGSTREAMIDENTIFY._serialized_start=957
  _LOGGINGSTREAMIDENTIFY._serialized_end=980
  _LOGGINGSTREAMIDENTITY._serialized_start=982
  _LOGGINGSTREAMIDENTITY._serialized_end=1065
  _LOGGINGCOLLECTOR._serialized_start=1067
  _LOGGINGCOLLECTOR._serialized_end=1187
# @@protoc_insertion_point(module_scope)
