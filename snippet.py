class Snippet:
    def __init__(self, id, samplingRate, textLength, text, textStartPosition, textEndPosition, percentageTotal,
                 audioLength, audioStartPosition, audioEndPosition):
        self.id = id
        self.samplingRate = samplingRate
        self.textLength = textLength
        self.text = text
        self.textStartPosition = textStartPosition
        self.textEndPosition = textEndPosition
        self.percentageTotal = percentageTotal
        self.audioLength = audioLength
        self.audioStartPosition = audioStartPosition
        self.audioEndPosition = audioEndPosition
