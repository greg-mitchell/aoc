(ns aoc.solution2022-6
  (:require [clojure.java.io :as io]
            [clojure.string :as s]))


(def input-file (io/resource "2022/6/input.txt"))
(def input-line
  (-> input-file
      slurp))

(def start-of-packet-re
  #"(.)(?!\1)(.)(?!\1|\2)(.)(?!\1|\2|\3)(.)")

(def packet-marker 
  (first (re-find start-of-packet-re input-line)))

(defn find-index-after
  [input marker]
  (+ (count marker) (s/index-of input marker)))

(def packet-start
  (find-index-after input-line packet-marker))

(def start-of-message-re
  #"(.)(?!\1)(.)(?!\1|\2)(.)(?!\1|\2|\3)(.)(?!\1|\2|\3|\4)(.)(?!\1|\2|\3|\4|\5)(.)(?!\1|\2|\3|\4|\5|\6)(.)(?!\1|\2|\3|\4|\5|\6|\7)(.)(?!\1|\2|\3|\4|\5|\6|\7|\8)(.)(?!\1|\2|\3|\4|\5|\6|\7|\8|\9)(?<ten>.)(?!\1|\2|\3|\4|\5|\6|\7|\8|\9|\k<ten>)(?<eleven>.)(?!\1|\2|\3|\4|\5|\6|\7|\8|\9|\k<ten>|\k<eleven>)(?<twelve>.)(?!\1|\2|\3|\4|\5|\6|\7|\8|\9|\k<ten>|\k<eleven>|\k<twelve>)(?<thirteen>.)(?!\1|\2|\3|\4|\5|\6|\7|\8|\9|\k<ten>|\k<eleven>|\k<twelve>|\k<thirteen>)(.)")

(def message-marker 
  (first (re-find start-of-message-re input-line)))

(def message-start
  (find-index-after input-line message-marker))

(defn match-and-find-message 
  [input]
  (find-index-after input (first (re-find start-of-message-re input))))