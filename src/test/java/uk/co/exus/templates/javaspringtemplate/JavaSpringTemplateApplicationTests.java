package uk.co.exus.templates.javaspringtemplate;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.assertTrue;

@SpringBootTest(properties = "spring.profiles.active:test")
class JavaSpringTemplateApplicationTests {

    @Test
    void contextLoads() {
        assertTrue(true);
    }

}
