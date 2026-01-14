package com.fieldguard.backend.model;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import java.time.LocalDateTime;

@Data
@Document(collection = "Alerts")
public class Alert {
    @Id
    private String id;
    private Integer animalId;
    private String severity;
    private String description;
    private LocalDateTime timestamp;

    private double temperature;
    private double heartRate;
    private double ruminationIndex;

}
