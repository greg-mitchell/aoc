(ns aoc.solution2022-1
  (:require [clojure.java.io :as io]
            [clojure.string :as s]))

(def input-file "2022/1/input.txt")
(defn input-lines []
  (-> input-file
      io/resource
      slurp 
      s/split-lines))

(defn parse-calories
  [lines]
  (let [loads (map #(if (= % "") -1 (Integer/parseInt %)) lines)
        loads (partition-by #(= -1 %) loads)
        loads (filter #(not (= % [-1])) loads)
        elves (map-indexed
               (fn [i load] {:load load 
                             :sum (apply + load)
                             :id (inc i)})
                   loads)]
    elves
    ))

(defn max-load
  [elves]
  (apply (partial max-key #(apply + (:load %))) elves))

(defn top-loads
  [elves n]
  (->> elves
       (sort-by :sum)
       reverse
       (take n)))

(defn sum-loads
  [elves]
  (->> elves
       (map :sum)
       (apply +)))