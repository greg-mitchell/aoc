(ns aoc.solution2022-2
  (:require [clojure.java.io :as io]
            [clojure.string :as s]))

(def input-file (io/resource "2022/2/input.txt"))
(def input-lines
  (-> input-file
      slurp
      s/split-lines))

(def decoder 
  {
   \A :rock
   \B :paper
   \C :sissors
   \X :rock
   \Y :paper
   \Z :sissors
   })

(def shape-score
  {
   :rock 1
   :paper 2
   :sissors 3
   })

(def outcomes 
  "from the perspective of you (column 2)"
  {
   [:rock :rock] 3
   [:rock :paper] 6
   [:rock :sissors] 0
   [:paper :rock] 0
   [:paper :paper] 3
   [:paper :sissors] 6
   [:sissors :rock] 6
   [:sissors :paper] 0
   [:sissors :sissors] 3
   })

(defn parse-lines
  [lines]
  (map (fn [line] 
         (vec (filter #(not (nil? %)) (map decoder line)))) 
       lines))

(def outcome-score
  (let [parsed-lines (-> input-lines parse-lines)]
    (+
     (->> parsed-lines (map outcomes) (apply +))
     (apply + (map #(shape-score (second %)) parsed-lines)))))

(def decoder2
  "X means you need to lose, Y means you need to end the round in a draw,
   and Z means you need to win."
  {"A X" [:rock :sissors]
   "A Y" [:rock :rock]
   "A Z" [:rock :paper]
   "B X" [:paper :rock]
   "B Y" [:paper :paper]
   "B Z" [:paper :sissors]
   "C X" [:sissors :paper]
   "C Y" [:sissors :sissors]
   "C Z" [:sissors :rock]})

(defn round-score
  [round]
  (+ (outcomes round) (shape-score (second round))))

(def answer2
  (->> input-lines (map decoder2) (map round-score) (apply +))
)