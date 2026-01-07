from django.urls import reverse
from playwright.sync_api import expect

from polymorphic.tests.utils import _GenericUITest
from .models import Project, ArtProject, ResearchProject


class ViewExampleTests(_GenericUITest):
    def test_view_example(self):
        """Test that the example view code works correctly."""
        # Step 1: Navigate to the type selection page
        select_url = f"{self.live_server_url}{reverse('project-select')}"
        self.page.goto(select_url)

        # Verify the page loaded
        expect(self.page).to_have_url(select_url)

        # Get model labels for the child models
        art_project_label = ArtProject._meta.label
        research_project_label = ResearchProject._meta.label

        # Verify radio buttons for both types exist
        art_radio = self.page.locator(f"input[type='radio'][value='{art_project_label}']")
        research_radio = self.page.locator(
            f"input[type='radio'][value='{research_project_label}']"
        )

        expect(art_radio).to_be_visible()
        expect(research_radio).to_be_visible()

        # Step 2: Select ArtProject and submit
        art_radio.click()
        self.page.click("button[type='submit']")

        # Should redirect to the create view with model parameter
        create_url_pattern = (
            f"{self.live_server_url}{reverse('project-create')}?model={art_project_label}"
        )
        expect(self.page).to_have_url(create_url_pattern)

        # Step 3: Fill in the ArtProject form
        # The form should have fields: topic (from Project) and artist (from ArtProject)
        self.page.fill("input[name='topic']", "Modern Art")
        self.page.fill("input[name='artist']", "Picasso")

        # Submit the form
        with self.page.expect_navigation(timeout=10000):
            self.page.click("button[type='submit']")

        # Verify the object was created
        art_project = ArtProject.objects.filter(topic="Modern Art", artist="Picasso").first()
        assert art_project is not None, "ArtProject was not created"
        assert art_project.topic == "Modern Art"
        assert art_project.artist == "Picasso"

        # Step 4: Test creating a ResearchProject
        self.page.goto(select_url)
        research_radio = self.page.locator(
            f"input[type='radio'][value='{research_project_label}']"
        )
        research_radio.click()
        self.page.click("button[type='submit']")

        # Verify redirect to create view
        create_url_pattern = (
            f"{self.live_server_url}{reverse('project-create')}?model={research_project_label}"
        )
        expect(self.page).to_have_url(create_url_pattern)

        # Fill in the ResearchProject form
        # Should have fields: topic and supervisor
        self.page.fill("input[name='topic']", "Quantum Computing")
        self.page.fill("input[name='supervisor']", "Dr. Smith")

        # Submit the form
        with self.page.expect_navigation(timeout=10000):
            self.page.click("button[type='submit']")

        # Verify the object was created
        research_project = ResearchProject.objects.filter(
            topic="Quantum Computing", supervisor="Dr. Smith"
        ).first()
        assert research_project is not None, "ResearchProject was not created"
        assert research_project.topic == "Quantum Computing"
        assert research_project.supervisor == "Dr. Smith"

        # Verify polymorphic querying works
        all_projects = Project.objects.all()
        assert all_projects.count() == 2
        assert isinstance(all_projects[0], (ArtProject, ResearchProject))
        assert isinstance(all_projects[1], (ArtProject, ResearchProject))
