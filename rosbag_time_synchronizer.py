import rosbag

from collections import namedtuple
import math


__all__ = ["MessagePack", "ApproximateTimeSynchronizer"]


MessagePack = namedtuple("MessagePack", "timestamp topic message")


class Filter(object):
    def __init__(self):
        self.callbacks = {}

    def register_callback(self, callback, *args):
        conn = len(self.callbacks)
        self.callbacks[conn] = (callback, args)
        return conn

    def signal_message(self, *msg):
        for cb, args in self.callbacks.values():
            cb(*(msg + args))


class MessagePackBuffer(object):
    """
    Stores a time history of messages.
    """
    def __init__(self, max_size):
        self.max_size = max_size
        self.timestamp_message_pack = {}
        self.topic_message_pack = {}

    def add(self, message_pack):
        self.timestamp_message_pack[message_pack.timestamp] = message_pack
        if message_pack.topic not in self.topic_message_pack:
            self.topic_message_pack[message_pack.topic] = []
        self.topic_message_pack[message_pack.topic].append(message_pack)

        if len(self.timestamp_message_pack) > self.max_size:
            oldest = min(self.timestamp_message_pack)
            self.delete_by_timestamp(oldest)

    def delete_by_timestamp(self, timestamp):
        if timestamp in self.timestamp_message_pack:
            topic = self.timestamp_message_pack[timestamp].topic
            del self.timestamp_message_pack[timestamp]
            for index, message_pack in enumerate(self.topic_message_pack[topic]):
                if message_pack.timestamp == timestamp:
                    del self.topic_message_pack[topic][index]

    def delete_by_topic(self, topic):
        if topic in self.topic_message_pack:
            timestamps = [message_pack.timestamp for message_pack in self.topic_message_pack[topic]]
            del self.topic_message_pack[topic]
            for timestamp in timestamps:
                del self.timestamp_message_pack[timestamp]


class ApproximateTimeSynchronizer(Filter):
    """
    Approximately synchronizes messages by their timestamps directly from a ROS bag.

    """
    def __init__(self, topics, max_delay=0.05, buffer_size=-1):
        """
        :param topics: messages to be synchronized
        :type topics: list of string
        :param max_delay: the delay (in seconds) with which messages can be synchronized
        :type max_delay: float
        :param buffer_size: max queue size of message buffer, if set to be -1, the size is double number of topics
        :type buffer_size: int
        """
        super(ApproximateTimeSynchronizer, self).__init__()
        self.__topics = topics
        self.__max_delay = max_delay
        self.__buffer_size = buffer_size if buffer_size != -1 else len(self.__topics) * 2
        self.__buffer = MessagePackBuffer(self.__buffer_size)

    def process_bag(self, ros_bag_file):
        """
        iterate over all messages in a given ROS bag. Ones messages are synchronized, callback will be invoked automatically.
        :param ros_bag_file: ROS bag file
        :type ros_bag_file: string
        """
        with rosbag.Bag(ros_bag_file) as bag:
            for topic, message, timestamp in bag.read_messages(topics=self.__topics):
                self.__buffer.add(MessagePack(timestamp, topic, message))
                contain, message_packs = self.__contains_all_desired_topics()
                if contain and self.__are_messages_well_synchronized(message_packs):
                    self.signal_message(*message_packs)
                    for message_pack in message_packs:
                        self.__buffer.delete_by_timestamp(message_pack.timestamp)

    def __contains_all_desired_topics(self):
        """
        check if the buffer contains all messages
        """
        contain = [False for _ in self.__topics]
        for i, topic in enumerate(self.__topics):
            if topic in self.__buffer.topic_message_pack and len(self.__buffer.topic_message_pack[topic]) > 0:
                contain[i] = True
        if all(contain):
            min_delay_timestamps = self.__find_min_delay_timestamp_set()
            message_packs = [self.__buffer.timestamp_message_pack[timestamp] for timestamp in min_delay_timestamps]
            return True, message_packs
        else:
            return False, []

    def __are_messages_well_synchronized(self, message_packs):
        """
        check if messages are well synchronized.
        """
        timestamps = [message_pack.timestamp.to_sec() for message_pack in message_packs]
        return (max(timestamps) - min(timestamps)) < self.__max_delay

    def __find_min_delay_timestamp_set(self):
        """
        TODO: make it more concise and clear
        """
        base_topic = self.__topics[0]
        base_timestamps = [message_pack.timestamp for message_pack in self.__buffer.topic_message_pack[base_topic]]
        delay_timestamps_list = []
        for base_timestamp in base_timestamps:
            sum_delay = 0.0
            timestamp_set = []
            for topic in self.__topics:
                timestamps = [message_pack.timestamp for message_pack in self.__buffer.topic_message_pack[topic]]
                delays = [math.fabs(base_timestamp.to_sec() - timestamp.to_sec())
                          for timestamp in timestamps]
                min_delay = min(delays)
                min_delay_index = delays.index(min_delay)
                sum_delay += min_delay
                timestamp_set.append(timestamps[min_delay_index])
            delay_timestamps_list.append((sum_delay, timestamp_set))
        sorted_delay_timestamps_list = sorted(delay_timestamps_list, key=lambda delay_timestamps: delay_timestamps[0])
        return sorted_delay_timestamps_list[0][1]


if __name__ == "__main__":
    def callback(msg_pack_1, msg_pack_2):
        timestamp_1 = msg_pack_1.timestamp
        topic_1 = msg_pack_1.topic
        message_1 = msg_pack_1.message

        timestamp_2 = msg_pack_2.timestamp
        topic_2 = msg_pack_2.topic
        message_2 = msg_pack_2.message

        # add your logic

    sync = ApproximateTimeSynchronizer(["/topics_1", "/topic_2"])
    sync.register_callback(callback)
    sync.process_bag("your/ros/bag/file")
